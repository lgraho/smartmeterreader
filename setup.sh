#!/bin/bash

# Install necessary packages
echo "Installing necessary packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Create a Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv ./venv

# Activate the virtual environment
source ./venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r ./requirements.txt

# Copy the systemd service file
echo "Setup systemd service..."
sudo cp ./scripts/smartmeter.service /etc/systemd/system/

# Make the scripts executable
sudo chmod +x ./scripts/start_service.sh
sudo chmod +x ./scripts/stop_service.sh
sudo chmod +x ./scripts/status_service.sh

echo "Setup complete. Please run the following command to start the service:"
echo "sudo ./scripts/start_service.sh"
