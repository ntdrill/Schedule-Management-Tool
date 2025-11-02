@echo off
echo スケジュール管理ツールを起動しています...
echo.

REM Python 3がインストールされているか確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3がインストールされていません。
    echo Python 3をインストールしてください。
    pause
    exit /b 1
)

echo ローカルサーバーを起動します...
echo ブラウザで http://localhost:8000 を開いてください
echo.
echo 終了するには Ctrl+C を押してください
echo.

REM HTTPサーバーを起動
python -m http.server 8000

pause
