"""
itdt.model: Implementación canónica del modelo basado en agentes ITDT (Secciones 3.1–3.4 y Tabla A1).
Sin cifras escritas a mano; todos los resultados emergen de la interacción de agentes y calibración SMM.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

from .parameters import FixedParameters, resolve_country_params
from .metrics import compute_monthly_metrics, aggregate_evaluation_window


class ITDTModel:
    """
    Modelo de Agentes ITDT para simulación de transiciones laborales y políticas de formalización.
    """

    def __init__(
        self,
        country_params: Union[str, Dict[str, Any]],
        scenario: str = "A",
        seed: int = 42,
        burn_in_months: int = 96,
        policy_months: int = 120,
        fixed_params: Optional[FixedParameters] = None,
        N_W: Optional[int] = None,
        N_F: Optional[int] = None,
    ):
        self.country_info = resolve_country_params(country_params)
        self.scenario = scenario.strip().upper()
        self.seed = int(seed)
        self.burn_in_months = int(burn_in_months)
        self.policy_months = int(policy_months)
        self.params = fixed_params or FixedParameters()

        if N_W is not None:
            self.params.N_W = int(N_W)
        if N_F is not None:
            self.params.N_F = int(N_F)

        # Generador pseudoaleatorio con semilla fija explícita
        self.rng = np.random.default_rng(self.seed)

        # Estado del modelo
        self.month = 0
        self.is_initialized = False
        self.reset()

    def reset(self):
        """Inicializa las poblaciones de trabajadores y empresas."""
        self.rng = np.random.default_rng(self.seed)
        self.month = 0
        p = self.params
        c = self.country_info

        N_W = p.N_W
        N_F = p.N_F

        # -------------------------------------------------------------
        # 1. POBLACIÓN DE TRABAJADORES (Sección 3.2)
        # -------------------------------------------------------------
        s_F = float(c["s_F"])
        # Sexo: g in {0, 1} con P(g=1) = s_F
        self.g = (self.rng.uniform(0.0, 1.0, N_W) < s_F).astype(int)

        # Educación: e in {0, 1, 2} con probabilidades (0.45, 0.40, 0.15)
        self.e = self.rng.choice([0, 1, 2], size=N_W, p=[0.45, 0.40, 0.15])

        # Zona: rural r in {0, 1} con P(r=1) = 0.60
        self.r = (self.rng.uniform(0.0, 1.0, N_W) < 0.60).astype(int)

        # Shocks de productividad y preferencia
        z_worker = self.rng.normal(0.0, 1.0, N_W)
        # Productividad h = exp(0.35*e - 0.20*r + 0.45*z), normalizada a media 1
        h_raw = np.exp(0.35 * self.e - 0.20 * self.r + 0.45 * z_worker)
        self.h = h_raw / np.mean(h_raw)

        # Precomputar bins y máscaras para evaluación rápida
        self.fem_mask = (self.g == 1)
        self.male_mask = (self.g == 0)
        self.rural_mask = (self.r == 1)
        self.urban_mask = (self.r == 0)
        self.edu_masks = {
            0: (self.e == 0),
            1: (self.e == 1),
            2: (self.e == 2)
        }
        quintile_cuts = np.percentile(self.h, [20, 40, 60, 80])
        self.quintile_bins = np.digitize(self.h, quintile_cuts) + 1
        self.precomputed_bins = {
            "fem_mask": self.fem_mask,
            "male_mask": self.male_mask,
            "rural_mask": self.rural_mask,
            "urban_mask": self.urban_mask,
            "edu_masks": self.edu_masks,
            "quintile_bins": self.quintile_bins,
        }

        # Horas de cuidado basales (Addati et al. 2018), truncadas en 0
        h_care_draw = np.where(
            self.fem_mask,
            self.rng.normal(p.H_care_fem_mean, p.H_care_fem_std, N_W),
            self.rng.normal(p.H_care_male_mean, p.H_care_male_std, N_W)
        )
        self.H_care_base = np.maximum(0.0, h_care_draw)
        self.H_care = self.H_care_base.copy()

        # Alfabetización digital K_dig in [0, 1]
        # Con determinantes sociodemográficos: educación, ruralidad y leve brecha de género
        k_dig_noise = self.rng.normal(0.0, 0.10, N_W)
        self.K_dig_w = np.clip(0.20 + 0.25 * self.e - 0.15 * self.r - 0.05 * self.g + k_dig_noise, 0.0, 1.0)

        # Preferencia por formalidad epsilon ~ N(0, 0.3^2) fija
        self.eps = self.rng.normal(0.0, p.eps_std, N_W)

        # Estado laboral de trabajadores: True = formal, False = informal
        self.worker_is_formal = np.zeros(N_W, dtype=bool)

        # -------------------------------------------------------------
        # 2. POBLACIÓN DE EMPRESAS (Sección 3.3)
        # -------------------------------------------------------------
        # Productividad A ~ LogNormal(0, 0.8^2)
        self.A = self.rng.lognormal(0.0, 0.80, N_F)

        # Capital ln K = 1 + 0.8*ln A + 0.3*z
        z_firm = self.rng.normal(0.0, 1.0, N_F)
        ln_K = 1.0 + 0.80 * np.log(self.A) + 0.30 * z_firm
        self.K = np.exp(ln_K)

        # Dueño asignado al azar de la población de trabajadores
        self.owners = self.rng.choice(N_W, size=N_F, replace=True)

        # Alfabetización digital de la empresa heredada del dueño
        self.K_dig_firm = self.K_dig_w[self.owners]

        # Parámetros calibrados
        self.phi_0 = float(c["phi_0"])
        self.gamma_0 = float(c["gamma_0"]) if p.care_enabled else 0.0

        # Estado del entorno digital D_sys
        self.d_sys = float(p.D_sys0)

        # Productividad efectiva inicial, demanda laboral y producción
        self._update_firm_production()

        # Condición inicial de empresas: formal si Pi_F > Pi_I (Apéndice A.1)
        self.is_formal_firm = self._evaluate_firm_profits(
            self.d_sys, p.kappa, p.phi_1, p.mu_0, p.mu_1, dcc_subsidy=False
        )[2]

        self._update_willing_workers(p.beta)
        self.monthly_history: List[Dict[str, Any]] = []
        self.is_initialized = True

    def _update_willing_workers(self, cur_beta: float):
        """Calcula la disposición de los trabajadores (U_F > U_I)."""
        p = self.params
        c_tr_effective = p.c_tr * (1.0 + self.r)
        if p.care_enabled and self.gamma_0 > 0:
            care_penalty_term = np.maximum(0.0, 1.0 - self.gamma_0 * (self.H_care / 48.0))
        else:
            care_penalty_term = 1.0

        net_formal_wage = p.omega_F * self.h * (1.0 - p.tau_w) * care_penalty_term
        arg_log = net_formal_wage - c_tr_effective
        valid_log = arg_log > 0.0

        U_F = np.where(
            valid_log,
            np.log(np.maximum(1e-9, arg_log)) + cur_beta + self.eps,
            -np.inf
        )
        U_I = np.log(p.omega_I * self.h)
        self.willing_workers = valid_log & (U_F > U_I)
        self.unwilling_mask = ~self.willing_workers
        self.num_willing = int(np.sum(self.willing_workers))

    def _update_firm_production(self):
        """Calcula A_tilde, L, Y y Y_bar para la población actual de empresas."""
        p = self.params
        owner_is_female = self.fem_mask[self.owners]
        owner_care = self.H_care[self.owners]

        # Si el cuidado está habilitado y la dueña es mujer:
        # A_tilde = A * (1 - 0.5 * gamma_0 * H_care / 48)
        if p.care_enabled and self.gamma_0 > 0:
            female_factor = np.maximum(1e-6, 1.0 - 0.5 * self.gamma_0 * (owner_care / 48.0))
            self.A_tilde = np.where(owner_is_female, self.A * female_factor, self.A)
        else:
            self.A_tilde = self.A.copy()

        # Demanda laboral L = min(40, max(1, round(0.5 * A_tilde^(1 / (1 - alpha)))))
        L_raw = 0.5 * (self.A_tilde ** (1.0 / (1.0 - p.alpha)))
        self.L = np.clip(np.round(L_raw).astype(int), 1, 40)

        # Función de producción: Cobb-Douglas (sigma=1.0) o CES (sigma != 1.0)
        if abs(p.ces_sigma - 1.0) < 1e-4:
            # Cobb-Douglas estándar: Y = 1.6 * A_tilde * L^alpha * K^(1 - alpha)
            self.Y = 1.6 * self.A_tilde * (self.L ** p.alpha) * (self.K ** (1.0 - p.alpha))
        else:
            # CES: Y = 1.6 * A_tilde * [alpha * L^rho + (1 - alpha) * K^rho]^(1/rho)
            rho_ces = (p.ces_sigma - 1.0) / p.ces_sigma
            ces_inner = p.alpha * (self.L ** rho_ces) + (1.0 - p.alpha) * (self.K ** rho_ces)
            self.Y = 1.6 * self.A_tilde * (np.maximum(1e-6, ces_inner) ** (1.0 / rho_ces))

        self.Y_bar = float(np.median(self.Y))

    def _evaluate_firm_profits(
        self,
        current_d_sys: float,
        current_kappa: float,
        current_phi_1: float,
        current_mu_0: float,
        current_mu_1: float,
        dcc_subsidy: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula Pi_F y Pi_I para todas las empresas bajo los parámetros activos.
        Devuelve (Pi_F, Pi_I, Pi_F > Pi_I).
        """
        p = self.params
        Y = self.Y
        Y_bar = self.Y_bar
        L = self.L
        K = self.K

        # 1. Costo digital de cumplimiento: DCC = Y_bar * [phi_0 + phi_1 * (Y_bar / Y)^eta * (1 - K_dig)]
        ratio = Y_bar / Y
        if p.regressive_dcc:
            DCC = Y_bar * (self.phi_0 + current_phi_1 * (ratio ** p.eta) * (1.0 - self.K_dig_firm))
        else:
            # Ablación: sin componente regresivo
            DCC = Y_bar * self.phi_0 * np.ones_like(Y)

        # Subsidio Escenario D: 80% al DCC para empresas con L <= 10
        if dcc_subsidy:
            DCC = np.where(L <= 10, DCC * 0.20, DCC)

        # 2. Probabilidad de auditoría: P_aud = 1 / (1 + exp(-kappa * (D_sys * Y/Y_bar - theta_th)))
        audit_arg = -current_kappa * (current_d_sys * (Y / Y_bar) - p.theta_th)
        P_aud = 1.0 / (1.0 + np.exp(np.clip(audit_arg, -50.0, 50.0)))

        # 3. Beneficios
        # Pi_F = (1 - tau_c)*Y - omega_F*(1 + tau_w)*L - r*K - DCC
        Pi_F = (1.0 - p.tau_c) * Y - p.omega_F * (1.0 + p.tau_w) * L - p.r_cred * K - DCC

        # Pi_I = Y - omega_I*L - r_I*K - P_aud*(mu_0*Y + mu_1*Y^xi)
        penalty = P_aud * (current_mu_0 * Y + current_mu_1 * (Y ** p.xi))
        Pi_I = Y - p.omega_I * L - p.r_I * K - penalty

        return Pi_F, Pi_I, (Pi_F > Pi_I)

    def step(self, record_metrics: bool = True) -> Optional[Dict[str, Any]]:
        """
        Ejecuta un paso mensual (t) siguiendo el orden exacto de procesos (Sección 3.4 y Figura 3).
        """
        p = self.params
        t = self.month
        in_policy = t >= self.burn_in_months

        # Inyección de choque de demanda en t = 96 + 60 = 156 (o demand_shock_month)
        if p.demand_shock_month is not None:
            shock_target = (
                p.demand_shock_month
                if p.demand_shock_month >= self.burn_in_months
                else (self.burn_in_months + p.demand_shock_month)
            )
            if t == shock_target:
                self.A = self.A * (1.0 + p.demand_shock_pct)
                self._update_firm_production()

        # Determinación de parámetros activos por escenario de política
        # NOTA: El multiplicador de sanciones (sanction_mult) actúa estrictamente en el período de política
        if not in_policy:
            cur_kappa = p.kappa
            cur_phi_1 = p.phi_1
            cur_mu_0 = p.mu_0
            cur_mu_1 = p.mu_1
            cur_beta = p.beta
            dcc_subsidy = False
            d_growth = p.D_sys_growth
        else:
            cur_kappa = p.kappa
            cur_phi_1 = p.phi_1
            cur_mu_0 = p.mu_0 * p.sanction_mult
            cur_mu_1 = p.mu_1 * p.sanction_mult
            cur_beta = p.beta
            dcc_subsidy = False
            d_growth = p.D_sys_growth

            sc = self.scenario
            if sc == "A" or sc == "BASELINE":
                d_growth = p.D_sys_growth
            elif sc == "B1":
                cur_kappa = p.kappa * 2.5
                d_growth = p.D_sys_growth * 3.0
                cur_phi_1 = p.phi_1 * 1.5
            elif sc == "B2":
                cur_kappa = p.kappa * 2.5
                d_growth = p.D_sys_growth * 3.0
                cur_phi_1 = p.phi_1 * 1.5
                cur_mu_0 = p.mu_0 * 3.0 * p.sanction_mult
                cur_mu_1 = p.mu_1 * 3.0 * p.sanction_mult
            elif sc == "C":
                d_growth = p.D_sys_growth
                # Reducción del 60% de horas de cuidado en mujeres
                if p.care_enabled and t == self.burn_in_months:
                    self.H_care = np.where(self.fem_mask, self.H_care_base * 0.40, self.H_care_base)
                    self._update_firm_production()
                    self._update_willing_workers(cur_beta)
            elif sc == "D":
                cur_kappa = p.kappa * 2.5
                d_growth = p.D_sys_growth * 3.0
                cur_phi_1 = p.phi_1 * 1.5
                cur_mu_0 = p.mu_0 * 3.0 * p.sanction_mult
                cur_mu_1 = p.mu_1 * 3.0 * p.sanction_mult
                dcc_subsidy = True
                cur_beta = p.beta * 1.5
                if t == self.burn_in_months:
                    if p.care_enabled:
                        self.H_care = np.where(self.fem_mask, self.H_care_base * 0.40, self.H_care_base)
                    self._update_firm_production()
                    self._update_willing_workers(cur_beta)

        # -------------------------------------------------------------
        # PASO 1: ENTORNO (D_sys crece)
        # -------------------------------------------------------------
        self.d_sys += d_growth

        # Calcular beneficios actuales
        Pi_F, Pi_I, _ = self._evaluate_firm_profits(
            current_d_sys=self.d_sys,
            current_kappa=cur_kappa,
            current_phi_1=cur_phi_1,
            current_mu_0=cur_mu_0,
            current_mu_1=cur_mu_1,
            dcc_subsidy=dcc_subsidy,
        )

        # -------------------------------------------------------------
        # PASO 2: REVISIÓN DE ESTADO (Prob 1/3, regla de Metropolis con Tk)
        # -------------------------------------------------------------
        N_F = p.N_F
        review_mask = self.rng.uniform(0.0, 1.0, N_F) < p.review_prob
        rho = (Pi_F - Pi_I) / self.Y

        if p.perfect_rationality:
            # Racionalidad perfecta (E2 / E4): cambian sin ruido estocástico
            switch_to_formal = review_mask & (~self.is_formal_firm) & (rho > 0.0)
            switch_to_informal = review_mask & self.is_formal_firm & (rho < 0.0)
            T_k = 0.0
        else:
            k_ann = t // 12
            T_k = p.T_0 * (p.d ** k_ann)
            prob_formalize = np.exp(np.minimum(rho, 0.0) / T_k)
            prob_informalize = np.exp(np.minimum(-rho, 0.0) / T_k)

            rand_draws = self.rng.uniform(0.0, 1.0, N_F)
            switch_to_formal = review_mask & (~self.is_formal_firm) & (rand_draws < prob_formalize)
            switch_to_informal = review_mask & self.is_formal_firm & (rand_draws < prob_informalize)

        self.is_formal_firm[switch_to_formal] = True
        self.is_formal_firm[switch_to_informal] = False

        # -------------------------------------------------------------
        # PASO 3: SALIDA Y REEMPLAZO POR ENTRANTES INFORMALES (Prob 0.10 si Pi < 0)
        # -------------------------------------------------------------
        current_profit = np.where(self.is_formal_firm, Pi_F, Pi_I)
        exit_mask = (current_profit < 0.0) & (self.rng.uniform(0.0, 1.0, N_F) < p.exit_prob)
        num_exits = int(np.sum(exit_mask))

        if num_exits > 0:
            # Reemplazo por entrantes informales
            A_new = self.rng.lognormal(0.0, 0.80, num_exits)
            z_new = self.rng.normal(0.0, 1.0, num_exits)
            ln_K_new = 1.0 + 0.80 * np.log(A_new) + 0.30 * z_new
            K_new = np.exp(ln_K_new)
            owners_new = self.rng.choice(p.N_W, size=num_exits, replace=True)

            self.A[exit_mask] = A_new
            self.K[exit_mask] = K_new
            self.owners[exit_mask] = owners_new
            self.K_dig_firm[exit_mask] = self.K_dig_w[owners_new]
            self.is_formal_firm[exit_mask] = False  # Entrante es estrictamente informal

            # Recomputar producción de la población
            self._update_firm_production()
            # Recomputar beneficios tras reemplazo
            Pi_F, Pi_I, _ = self._evaluate_firm_profits(
                current_d_sys=self.d_sys,
                current_kappa=cur_kappa,
                current_phi_1=cur_phi_1,
                current_mu_0=cur_mu_0,
                current_mu_1=cur_mu_1,
                dcc_subsidy=dcc_subsidy,
            )

        # -------------------------------------------------------------
        # PASO 4: DISPOSICIÓN DE LOS TRABAJADORES (U_F > U_I)
        # -------------------------------------------------------------
        willing_workers = self.willing_workers

        # -------------------------------------------------------------
        # PASO 5: ASIGNACIÓN DE VACANTES FORMALES POR RANKING DE PRODUCTIVIDAD
        # -------------------------------------------------------------
        vacancies = int(np.sum(self.L[self.is_formal_firm]))
        
        # Ruido multiplicativo uniforme de +/- 10%
        noise_10 = self.rng.uniform(-0.10, 0.10, p.N_W)
        ranking_score = self.h * (1.0 + noise_10)
        # Quienes no están dispuestos no compiten por vacantes formales
        ranking_score[self.unwilling_mask] = -np.inf

        self.worker_is_formal.fill(False)
        if vacancies > 0 and self.num_willing > 0:
            num_to_hire = min(vacancies, self.num_willing)
            # Selección de los mejores num_to_hire trabajadores
            top_candidate_indices = np.argpartition(-ranking_score, num_to_hire - 1)[:num_to_hire]
            self.worker_is_formal[top_candidate_indices] = True

        # -------------------------------------------------------------
        # PASO 6: RESOLUCIÓN DE ESTADO LABORAL
        # El resto es informal o cuenta propia; los dueños de empresas formales son formales
        # -------------------------------------------------------------
        formal_owners = self.owners[self.is_formal_firm]
        self.worker_is_formal[formal_owners] = True

        self.month += 1

        # -------------------------------------------------------------
        # PASO 7: REGISTRO DE MÉTRICAS MENSUALES (si está habilitado)
        # -------------------------------------------------------------
        if record_metrics:
            care_penalty = (
                np.maximum(0.0, 1.0 - self.gamma_0 * (self.H_care / 48.0))
                if (p.care_enabled and self.gamma_0 > 0)
                else np.ones_like(self.h)
            )
            record = compute_monthly_metrics(
                month=t,
                is_burn_in=not in_policy,
                worker_is_formal=self.worker_is_formal,
                g=self.g,
                e=self.e,
                r=self.r,
                h=self.h,
                is_formal_firm=self.is_formal_firm,
                Y=self.Y,
                L=self.L,
                num_exits=num_exits,
                tau_c=p.tau_c,
                tau_w=p.tau_w,
                omega_F=p.omega_F,
                d_sys=self.d_sys,
                T_k=T_k,
                willing_workers=willing_workers,
                precomputed_bins=self.precomputed_bins,
                care_penalty=care_penalty,
            )
            self.monthly_history.append(record)
            return record

        return None

    def simulate_moments(self, burn_in_months: int = 96, eval_months: int = 24) -> Tuple[float, float]:
        """
        Ejecución acelerada para calibración SMM.
        Corre burn_in_months sin registro detallado y eval_months acumulando solo tasas F y M.
        Devuelve (F_sim_pct, M_sim_pct).
        """
        # 1. Calentamiento rápido
        for _ in range(burn_in_months):
            self.step(record_metrics=False)

        # 2. Evaluación de los siguientes eval_months
        f_rates = []
        m_rates = []
        for _ in range(eval_months):
            self.step(record_metrics=False)
            f_rate = (1.0 - np.mean(self.worker_is_formal[self.fem_mask])) * 100.0
            m_rate = (1.0 - np.mean(self.worker_is_formal[self.male_mask])) * 100.0
            f_rates.append(f_rate)
            m_rates.append(m_rate)

        return float(np.mean(f_rates)), float(np.mean(m_rates))

    def run(self) -> Dict[str, Any]:
        """
        Ejecuta la simulación completa (burn-in + período de política).
        Devuelve series mensuales y métricas agregadas.
        """
        total_months = self.burn_in_months + self.policy_months
        while self.month < total_months:
            self.step(record_metrics=True)

        # Resumen sobre los últimos 12 meses de política (meses 109 a 120 de la política)
        summary = aggregate_evaluation_window(self.monthly_history, window_size=12)

        return {
            "country": self.country_info.get("name", "Custom"),
            "country_code": self.country_info.get("country_code", "XXX"),
            "scenario": self.scenario,
            "seed": self.seed,
            "burn_in_months": self.burn_in_months,
            "policy_months": self.policy_months,
            "total_months_simulated": len(self.monthly_history),
            "monthly_series": self.monthly_history,
            "summary_metrics": summary,
        }


def run(
    country_params: Union[str, Dict[str, Any]],
    scenario: str = "A",
    seed: int = 42,
    months: int = 120,
    burn_in_months: int = 96,
    fixed_params: Optional[FixedParameters] = None,
) -> Dict[str, Any]:
    """
    Función de API pública para ejecutar una simulación del modelo ITDT.

    Parámetros:
    - country_params: Nombre del país ('KENYA', 'NIGERIA', 'INDIA', 'BANGLADESH')
                      o diccionario con {'s_F': float, 'phi_0': float, 'gamma_0': float}.
    - scenario: 'A' (Status Quo), 'B1' (GovTech moderado), 'B2' (GovTech intensivo),
                'C' (Red de cuidados), 'D' (Integrado).
    - seed: Semilla pseudoaleatoria explícita (e.g. 20260).
    - months: Duración en meses de la política (default: 120 meses).
    - burn_in_months: Período de calentamiento previo (default: 96 meses).
    - fixed_params: Instancia opcional de FixedParameters para sensibilidad/ablación.

    Retorna:
    Diccionario con 'monthly_series' (registro mes a mes) y 'summary_metrics' (promedio final).
    """
    model = ITDTModel(
        country_params=country_params,
        scenario=scenario,
        seed=seed,
        burn_in_months=burn_in_months,
        policy_months=months,
        fixed_params=fixed_params,
    )
    return model.run()
