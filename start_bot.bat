@echo off
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей. Проверьте подключение к интернету и права доступа.
    pause
    exit
)
python bot.py
pause