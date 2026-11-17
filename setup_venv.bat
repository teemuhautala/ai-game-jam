@echo off
setlocal

REM Always run from the project root (where this script is located).
cd /d "%~dp0"

set "VENV_DIR=.venv"

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>&1
    if not %errorlevel%==0 (
        echo Error: Python 3 was not found in PATH.
        exit /b 1
    )
    set "PY_CMD=python"
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment in %VENV_DIR%...
    %PY_CMD% -m venv "%VENV_DIR%"
    if not %errorlevel%==0 exit /b 1
) else (
    echo Using existing virtual environment in %VENV_DIR%...
)

"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if not %errorlevel%==0 exit /b 1

"%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
if not %errorlevel%==0 exit /b 1

echo.
echo Done. Activate it with:
echo   .venv\Scripts\activate

endlocal
