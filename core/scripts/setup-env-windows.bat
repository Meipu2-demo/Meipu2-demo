@echo off
chcp 65001
rem Windows環境変数設定スクリプト
rem 使用方法: setup-env-windows.bat を実行してから他のコマンドを実行

rem 仮想環境を有効化

rem 環境変数を設定
set MEIPU_ROOT_PATH=%CD%

rem .envファイルから環境変数を読み込み
if exist .env (
    call :load_env_var MEIPU_GEMINI_API_KEY
    call :load_env_var USE_OLLAMA
    call :load_env_var OLLAMA_BASE_URL
    call :load_env_var OLLAMA_MODEL
    call :load_env_var OLLAMA_TIMEOUT_SEC
)

if not defined USE_OLLAMA set USE_OLLAMA=False
if not defined OLLAMA_BASE_URL set OLLAMA_BASE_URL=http://127.0.0.1:11434
if not defined OLLAMA_MODEL set OLLAMA_MODEL=gemma3:12b
if not defined OLLAMA_TIMEOUT_SEC set OLLAMA_TIMEOUT_SEC=120

echo 環境変数が設定されました
echo MEIPU_ROOT_PATH=%MEIPU_ROOT_PATH%
@REM echo MEIPU_GEMINI_API_KEY=%MEIPU_GEMINI_API_KEY%
echo USE_OLLAMA=%USE_OLLAMA%
@REM echo OLLAMA_BASE_URL=%OLLAMA_BASE_URL%
echo OLLAMA_MODEL=%OLLAMA_MODEL%
echo OLLAMA_TIMEOUT_SEC=%OLLAMA_TIMEOUT_SEC%
echo.
echo この環境でコマンドを実行してください
echo 例: .\core\scripts\julius-windows.bat
echo 例: .\MMDAgent-EX\MMDAgent-EX.exe .\meipu-contents\main.mdf

call .venv\Scripts\activate.bat

cmd /k
goto :eof

:load_env_var
for /f "tokens=2 delims==" %%i in ('findstr /r /b /c:"%~1=" /c:"export %~1=" .env') do set "%~1=%%i"
exit /b
