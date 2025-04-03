@echo off

:: Get the directory of the script and change to it
cd /d "%~dp0"

:: Create a folder called 'secrets' if it doesn't exist
if not exist secrets mkdir secrets

:: Generate password for data generator
powershell -Command "[System.Guid]::NewGuid().ToString() | Set-Content -Path 'secrets/iot_temp_data_gen_password.txt' -NoNewline"

:: Generate password for web viewer
powershell -Command "[System.Guid]::NewGuid().ToString() | Set-Content -Path 'secrets/iot_temp_web_view_password.txt' -NoNewline"

echo Accounts created! Starting IoT weather app...

:: Run Docker Compose to start up the containers
:: docker-compose up -d

:: Print message after Docker Compose runs
echo Docker Compose has been executed. The containers are now up and running.
echo You can access the web app at http://localhost:8080.
