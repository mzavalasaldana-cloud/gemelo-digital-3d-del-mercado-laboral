@echo off
if "%~1"=="" goto help
if "%~1"=="help" goto help
if "%~1"=="ia" goto ia
if "%~1"=="owner" goto owner
if "%~1"=="figuras" goto figuras
if "%~1"=="all" goto all

python -m itdt.cli %*
goto end

:help
python -m itdt.cli help
echo   owner        - Cierres anuales y formalizacion por sexo del dueno (3 modos)
echo   figuras      - Genera las figuras del articulo en espanol e ingles (PNG y PDF)
goto end

:ia
python scripts/entrenar_motor_ia.py
goto end

:owner
python scripts/cierres_por_dueno.py
python scripts/cierres_por_dueno.py --modo ablacion
python scripts/cierres_por_dueno.py --modo especificaciones
goto end

:figuras
python scripts/generar_figuras.py
python scripts/generar_figuras_en.py
goto end

:all
python -m itdt.cli all
python scripts/cierres_por_dueno.py
python scripts/cierres_por_dueno.py --modo ablacion
python scripts/cierres_por_dueno.py --modo especificaciones
python scripts/generar_figuras.py
python scripts/generar_figuras_en.py
goto end

:end
