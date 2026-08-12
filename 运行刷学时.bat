@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON%" goto run

set "PYTHON=%LocalAppData%\Programs\Python\Python312\python.exe"
if exist "%PYTHON%" goto run

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -u main.py
    goto end
)

where python >nul 2>nul
if not errorlevel 1 (
    python -u main.py
    goto end
)

echo Python 3 was not found.
echo Please install Python 3.10 or newer.
pause
goto end

:run
"%PYTHON%" -u main.py

:end
echo.
echo.
echo Program ended. Press any key to close.
pause >nul
