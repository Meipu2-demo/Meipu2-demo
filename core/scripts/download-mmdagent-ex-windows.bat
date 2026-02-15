@echo off
setlocal

rem Download and extract MMDAgent-EX release package for Windows

set "MMDAGENT_EX_URL=https://github.com/mmdagent-ex/MMDAgent-EX/releases/download/v2.1/MMDAgent-EX-x64-v2.1.zip"
set "ZIP_FILE=MMDAgent-EX-x64-v2.1.zip"
set "TMP_DIR=MMDAgent-EX-tmp"
set "TARGET_DIR=MMDAgent-EX"

echo Starting MMDAgent-EX setup...

rem Check if we're in the correct directory
if not exist "pyproject.toml" (
    echo Error: Please run this script from the Meipu2-demo root directory
    exit /b 1
)

rem Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is required but not found
    exit /b 1
)

if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
if exist "%TARGET_DIR%" rmdir /s /q "%TARGET_DIR%"

echo Downloading MMDAgent-EX release...
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%MMDAGENT_EX_URL%' -OutFile '%ZIP_FILE%'"
if %errorlevel% neq 0 (
    echo Error: Failed to download MMDAgent-EX release
    exit /b 1
)

echo Extracting archive...
powershell -NoProfile -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%TMP_DIR%' -Force"
if %errorlevel% neq 0 (
    echo Error: Failed to extract MMDAgent-EX archive
    exit /b 1
)

echo Preparing MMDAgent-EX directory...
powershell -NoProfile -Command "$items = Get-ChildItem -LiteralPath '%TMP_DIR%'; if ($items.Count -eq 1 -and $items[0].PSIsContainer) { Move-Item -LiteralPath $items[0].FullName -Destination '%TARGET_DIR%' } else { New-Item -ItemType Directory -Path '%TARGET_DIR%' | Out-Null; Move-Item -Path (Join-Path '%TMP_DIR%' '*') -Destination '%TARGET_DIR%' }"
if %errorlevel% neq 0 (
    echo Error: Failed to prepare MMDAgent-EX directory
    exit /b 1
)

if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"

echo MMDAgent-EX setup completed successfully.
endlocal
