@echo off
if "%~1"=="" (
    python -m itdt.cli help
) else if "%~1"=="ia" (
    python scripts/entrenar_motor_ia.py
) else (
    python -m itdt.cli %*
)
