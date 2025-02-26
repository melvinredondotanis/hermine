#!/bin/bash

set -e

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

REPO_DIR=$(pwd)
CONFIG_DIR="$REPO_DIR/config"
DEST_CONFIG_DIR="/etc/hermine"
INSTALL_DIR="/opt/hermine"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="hermine"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# Check for dependencies
echo "Checking for dependencies..."
for cmd in python3 pip3 virtualenv; do
    if ! command -v $cmd &> /dev/null; then
        echo "$cmd is required but not installed. Aborting." >&2
        exit 1
    fi
done

# Create the destination directories
echo "Creating directories..."
mkdir -p $DEST_CONFIG_DIR
mkdir -p $INSTALL_DIR

# Copy configuration files
echo "Copying configuration files..."
if [ -d "$CONFIG_DIR" ]; then
    cp -r "$CONFIG_DIR"/* $DEST_CONFIG_DIR/
else
    echo "Warning: Config directory not found at $CONFIG_DIR"
fi

# Create virtual environment
echo "Creating virtual environment..."
virtualenv $VENV_DIR -p python3

# Install the project
echo "Installing the project..."
cp -r "$REPO_DIR"/* $INSTALL_DIR/
source $VENV_DIR/bin/activate
pip install --upgrade pip

# Check for Python dependencies
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install -r "$INSTALL_DIR/requirements.txt"
elif [ -f "$INSTALL_DIR/setup.py" ] || [ -f "$INSTALL_DIR/pyproject.toml" ]; then
    echo "Installing project in development mode..."
    pip install -e "$INSTALL_DIR"
else
    echo "No Python package configuration found. Skipping pip install."
fi

deactivate


# Create systemd service file
echo "Creating systemd service..."
cat > $SERVICE_FILE << EOL
[Unit]
Description=Hermine Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/daemon/app.py
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
echo "Setting permissions..."
chmod 644 $SERVICE_FILE
chmod 755 $INSTALL_DIR/Modelfile
if [ -f "$INSTALL_DIR/daemon/app.py" ]; then
    chmod +x $INSTALL_DIR/daemon/app.py
else
    echo "Warning: $INSTALL_DIR/daemon/app.py does not exist. Make sure your app entry point is correctly specified in the service file."
    mkdir -p "$INSTALL_DIR/daemon"
    touch "$INSTALL_DIR/daemon/app.py"
    chmod +x "$INSTALL_DIR/daemon/app.py"
    echo "#!/usr/bin/env python3\nprint('Hello from Hermine!')" > "$INSTALL_DIR/daemon/app.py"
fi
chown -R root:root $INSTALL_DIR
chown -R root:root $DEST_CONFIG_DIR

# Enable and start the service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Installation completed successfully!"
echo "Service status: $(systemctl is-active $SERVICE_NAME)"
echo "To check the logs: journalctl -u $SERVICE_NAME"
