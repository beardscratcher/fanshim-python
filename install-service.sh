#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LIBRARY_DIR="$DIR/library"
VENV_PATH="/opt/fanshim-venv"
SERVICE_PATH=/etc/systemd/system/pimoroni-fanshim.service
SERVICE_NAME=pimoroni-fanshim.service

SPEED_STEPS="40:0,50:50,58:100"
MIN_SPEED=20
DELAY=2
BRIGHTNESS=128
NOLED="no"

USAGE="sudo ./install-service.sh [--speed-steps <steps>] [--min-speed <n>] [--delay <n>] [--brightness <n>] [--noled] [--venv <path>]"

while [[ $# -gt 0 ]]; do
    case "$1" in
    --speed-steps)
        SPEED_STEPS="$2"; shift 2;;
    --min-speed)
        MIN_SPEED="$2"; shift 2;;
    --delay)
        DELAY="$2"; shift 2;;
    --brightness)
        BRIGHTNESS="$2"; shift 2;;
    --noled)
        NOLED="yes"; shift;;
    --venv)
        VENV_PATH="$(realpath "${2%/}")"; shift 2;;
    *)
        printf "Unrecognised option: %s\nUsage: %s\n" "$1" "$USAGE"; exit 1;;
    esac
done

EXTRA_ARGS=""
if [ "$NOLED" == "yes" ]; then EXTRA_ARGS+=" --noled"; fi

cat <<EOF
Fan Shim service setup:
  Speed steps : $SPEED_STEPS
  Min speed   : $MIN_SPEED %
  Delay       : $DELAY s
  Brightness  : $BRIGHTNESS
  Disable LED : $NOLED
  Venv        : $VENV_PATH
  Service     : $SERVICE_PATH

EOF

# Stop and disable old service if present
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    printf "Stopping existing service...\n"
    systemctl stop "$SERVICE_NAME"
fi
if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    printf "Disabling existing service...\n"
    systemctl disable "$SERVICE_NAME"
fi

# System dependencies via apt
printf "Installing system dependencies...\n"
apt-get install -y python3-lgpio python3-rpi.gpio python3-psutil python3-venv python3-spidev build-essential python3-dev

# Create venv with access to apt-installed packages
printf "Creating venv at %s...\n" "$VENV_PATH"
python3 -m venv --system-site-packages "$VENV_PATH"

# Install fanshim library from local source into venv
printf "Installing fanshim library...\n"
"$VENV_PATH/bin/pip3" install --quiet "$LIBRARY_DIR"

# Write systemd unit
printf "Writing service unit to %s...\n" "$SERVICE_PATH"
cat > "$SERVICE_PATH" <<UNIT
[Unit]
Description=Fan Shim Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=$VENV_PATH/bin/python3 $DIR/automatic.py --speed-steps "$SPEED_STEPS" --min-speed "$MIN_SPEED" --delay "$DELAY" --brightness "$BRIGHTNESS"$EXTRA_ARGS
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

# Enable and start
systemctl daemon-reload
systemctl enable --no-pager "$SERVICE_NAME"
systemctl restart --no-pager "$SERVICE_NAME"
systemctl status --no-pager "$SERVICE_NAME"
