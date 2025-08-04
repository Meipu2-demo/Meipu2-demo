@echo off
rem External components download script for Meipu2-demo (Windows)
rem This script downloads contents (example) and dictation-kit

echo Starting external components download...

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

rem Function to download and extract using PowerShell
call :download_and_extract "contents.zip" "https://github.com/mmdagent-ex/example/archive/95e3a0b389be60d5c8fd0215684f82512cb81d36.zip" "example-95e3a0b389be60d5c8fd0215684f82512cb81d36" "contents"

rem Download gene submodule
call :download_and_extract "gene.zip" "https://github.com/mmdagent-ex/gene/archive/c7eace43dffaccff6ad0597433ef85fa57c91e03.zip" "gene-c7eace43dffaccff6ad0597433ef85fa57c91e03" "contents\gene"

rem Download dictation-kit
call :download_and_extract "dictation-kit.zip" "https://github.com/julius-speech/dictation-kit/archive/1ceb4dec245ef482918ca33c55c71d383dce145e.zip" "dictation-kit-1ceb4dec245ef482918ca33c55c71d383dce145e" "dictation-kit"

echo All external components downloaded successfully!
goto :eof

:download_and_extract
set "filename=%~1"
set "url=%~2"
set "extract_name=%~3"
set "target_name=%~4"

echo Downloading %filename%...
powershell -Command "Invoke-WebRequest -Uri '%url%' -OutFile '%filename%'"

echo Extracting %filename%...
powershell -Command "Expand-Archive -Path '%filename%' -DestinationPath '.' -Force"

rem Move and rename
if exist "%extract_name%" (
    if exist "%target_name%" (
        rmdir /s /q "%target_name%"
    )
    move "%extract_name%" "%target_name%"
)

rem Clean up
if exist "%filename%" (
    del "%filename%"
)

echo Setup complete for %target_name%
goto :eof