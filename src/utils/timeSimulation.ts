export const TOTAL_SIMULATION_MONTHS = 120; // 10 years * 12 months = 120 months

export const MONTH_NAMES_ES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

export const MONTH_NAMES_EN = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

/**
 * Formats a month index (0 to 120) into a readable timeline string.
 * Example: 42, 'es' -> "Mes 42 - Junio 2027"
 * Example: 42, 'en' -> "Month 42 - June 2027"
 */
export function formatSimMonth(monthIndex: number, lang: 'es' | 'en' = 'es', startYear = 2024): string {
  const clamped = Math.max(0, Math.min(TOTAL_SIMULATION_MONTHS, Math.round(monthIndex)));
  const year = startYear + Math.floor(clamped / 12);
  const names = lang === 'en' ? MONTH_NAMES_EN : MONTH_NAMES_ES;
  const monthName = names[clamped % 12];
  const prefix = lang === 'en' ? 'Month' : 'Mes';
  return `${prefix} ${clamped} - ${monthName} ${year}`;
}

export function getSimYear(monthIndex: number, startYear = 2024): number {
  return startYear + Math.floor(Math.max(0, monthIndex) / 12);
}

export function getSimMonthName(monthIndex: number, lang: 'es' | 'en' = 'es'): string {
  const clamped = Math.max(0, Math.min(TOTAL_SIMULATION_MONTHS, Math.round(monthIndex)));
  const names = lang === 'en' ? MONTH_NAMES_EN : MONTH_NAMES_ES;
  return names[clamped % 12];
}
