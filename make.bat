@echo off
if "%~1"=="" (
    python -m itdt.cli help
) else (
    python -m itdt.cli %*
)
