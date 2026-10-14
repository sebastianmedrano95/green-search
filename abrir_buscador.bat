@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "APP=%SCRIPT_DIR%interfaz.py"
set "PYTHON="

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Python\python.exe" set "PYTHON=%LOCALAPPDATA%\Python\python.exe"
if not defined PYTHON if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if defined PYTHON goto launch

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py"
    goto launch
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=python"
    goto launch
)

:error
echo No se pudo iniciar el buscador.
echo No se encontro una instalacion de Python. Instala Python 3 y activa la opcion Add Python to PATH.
echo.
pause
exit /b 1

:launch
"%PYTHON%" -m pip show pywebview >nul 2>nul
if errorlevel 1 (
    echo Instalando la interfaz pywebview por primera vez...
    "%PYTHON%" -m pip install pywebview
    if errorlevel 1 goto dependency_error
)
"%PYTHON%" "%APP%"
if errorlevel 1 goto startup_error
exit /b 0

:dependency_error
echo No se pudo instalar pywebview con:
echo "%PYTHON%"
echo Verifica tu conexion a Internet y vuelve a intentarlo.
pause
exit /b 1

:startup_error
echo Green Search se cerro con un error. El mensaje aparece arriba.
pause
exit /b 1
