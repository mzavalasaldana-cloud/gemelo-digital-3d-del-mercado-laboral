.PHONY: all smoke calibrate calib_se loco baselines sweep scenarios mechanism sensitivity cost clean help

PYTHON ?= python

help:
	@echo "======================================================================"
	@echo " ITDT: Paquete de Replicación del Artículo"
	@echo "======================================================================"
	@echo "Comandos disponibles:"
	@echo "  make smoke        - Pruebas unitarias, metamórficas y corrida rápida (< 1 min)"
	@echo "  make calibrate    - Calibración SMM basal (Tablas 2 y 11, Figura 4)"
	@echo "  make calib_se     - Calibración con errores estándar (10 conjuntos de semillas)"
	@echo "  make loco         - Validación fuera de muestra LOCO (Tabla 3, loco_insumos.md)"
	@echo "  make baselines    - Modelos de referencia E1–E4 dentro de muestra (Tabla 4)"
	@echo "  make sweep        - Barrido de intensidad de sanciones 1 a 4 bajo B1 (Figura 5)"
	@echo "  make scenarios    - Escenarios A, B1, B2, C, D (Tablas 5, 6, 7, Figuras 6 y 7)"
	@echo "  make mechanism    - Ablación de B2 frente a A con recalibración (Tabla 8)"
	@echo "  make sensitivity  - Sensibilidad +-20%, CES y choque de demanda (Tabla 9)"
	@echo "  make cost         - Benchmarking de costo computacional (Tabla 10)"
	@echo "  make all          - Regenera outputs/ desde cero y reporta el tiempo total"
	@echo "  make clean        - Limpia outputs/ y cachés de Python"
	@echo "======================================================================"

smoke:
	$(PYTHON) -m itdt.cli smoke

calibrate:
	$(PYTHON) -m itdt.cli calibrate

calib_se:
	$(PYTHON) -m itdt.cli calib_se

loco:
	$(PYTHON) -m itdt.cli loco

baselines:
	$(PYTHON) -m itdt.cli baselines

sweep:
	$(PYTHON) -m itdt.cli sweep

scenarios:
	$(PYTHON) -m itdt.cli scenarios

mechanism:
	$(PYTHON) -m itdt.cli mechanism

sensitivity:
	$(PYTHON) -m itdt.cli sensitivity

cost:
	$(PYTHON) -m itdt.cli cost

all:
	$(PYTHON) -m itdt.cli all

clean:
	$(PYTHON) -c "import shutil, os; [shutil.rmtree(d, ignore_errors=True) for d in ['outputs', '.pytest_cache', 'itdt/__pycache__', 'tests/__pycache__']]"
