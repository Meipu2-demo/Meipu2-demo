@echo off
chcp 65001
rem Windows環境変数設定スクリプト
rem 使用方法: setup-env-windows.bat を実行してから他のコマンドを実行

rem 仮想環境を有効化

rem 環境変数を設定
set MEIPU_ROOT_PATH=%CD%

rem .envファイルからGemini APIキーを読み込み
if exist .env (
    for /f "tokens=2 delims==" %%i in ('findstr "MEIPU_GEMINI_API_KEY" .env') do set MEIPU_GEMINI_API_KEY=%%i
)

echo 環境変数が設定されました
echo MEIPU_ROOT_PATH=%MEIPU_ROOT_PATH%
@REM echo MEIPU_GEMINI_API_KEY=%MEIPU_GEMINI_API_KEY%
echo.
echo この環境でコマンドを実行してください
echo 例: core\scripts\julius-windows.bat

call .venv\Scripts\activate.bat

cmd /k