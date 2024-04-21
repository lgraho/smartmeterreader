#!/bin/bash
if systemctl is-active smartmeter.service >/dev/null 2>&1; then
    echo "Smart Meter service is running."
else
    echo "Smart Meter service is not running."
fi