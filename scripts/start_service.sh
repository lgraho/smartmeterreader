#!/bin/bash
echo "Starting the Smart Meter service..."
sudo systemctl daemon-reload
sudo systemctl enable smartmeter.service
sudo systemctl start smartmeter.service
sudo ./scripts/status_service.sh
