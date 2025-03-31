#!/bin/bash

# Get the directory of the script and change to it
cd "$(dirname "$0")" || exit

# Create a folder called 'secrets' if it doesn't exist
mkdir -p secrets

# Generate password for iot_temp_admin_password
uuidgen > secrets/iot_temp_admin_password.txt

# Generate password for iot_temp_data_gen_password
uuidgen > secrets/iot_temp_data_gen_password.txt

# Generate password for iot_temp_web_viewer_password
uuidgen > secrets/iot_temp_web_viewer_password.txt

echo "Accounts created! Starting IoT weather app..."

# Run Docker Compose to start up the containers
docker-compose up -d

# Print message after Docker Compose runs
echo "Docker Compose has been executed. The containers are now up and running."
echo "You can access the web app at http://localhost:8080."
