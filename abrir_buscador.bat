@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP=%SCRIPT_DIR%buscador.py"

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py"
    call :launch
    exit /b 0
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=python"
    call :launch
    exit /b 0
)

:error
echo No se pudo iniciar el buscador.
echo.
echo Si aparece un error arriba, toma una foto o copia el mensaje.
pause
exit /b 1

:launch
%PYTHON% -m pip show pywebview >nul 2>nul
if errorlevel 1 (
    echo Instalando la interfaz pywebview por primera vez...
    %PYTHON% -m pip install pywebview
    if errorlevel 1 goto error
)
%PYTHON% "%APP%"
if errorlevel 1 goto error
exit /b 0
