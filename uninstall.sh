#!/bin/bash

set -e

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

# Define the same variables as in the install script
DEST_CONFIG_DIR="/etc/hermine"
INSTALL_DIR="/opt/hermine"
SERVICE_NAME="hermine"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Uninstalling Hermine..."

# Stop and disable the service
echo "Stopping and disabling the service..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    systemctl disable "$SERVICE_NAME"
fi

# Remove the service file
echo "Removing service file..."
if [ -f "$SERVICE_FILE" ]; then
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload
fi

# Remove installation directories
echo "Removing installed files..."
if [ -d "$DEST_CONFIG_DIR" ]; then
    rm -rf "$DEST_CONFIG_DIR"
fi

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

echo "Uninstallation completed successfully!"
