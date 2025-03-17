@echo off
echo Starting Flask app and Telegram bot...
start cmd /k "cd c:\Users\PC\Downloads\fraud-report-systemV9\fraud-report-systemV11\fraud-report-systemV12 && python app.py"
start cmd /k "cd c:\Users\PC\Downloads\fraud-report-systemV9\fraud-report-systemV11\fraud-report-systemV12 && python run_telegram_bot.py"
echo Both applications are now running in separate windows.
