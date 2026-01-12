#!/bin/bash
# Installation script for Bernese Word Clock on Raspberry Pi
# This script installs the rpi-rgb-led-matrix library and Python bindings

set -e

echo "=========================================="
echo "  Bärner Wort-Uhr Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi."
    echo "The LED matrix library may not work correctly."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install dependencies
echo "Installing dependencies..."
sudo apt-get install -y \
    git \
    python3-dev \
    python3-pip \
    libgraphicsmagick++-dev \
    libwebp-dev

# Clone and build rpi-rgb-led-matrix
MATRIX_DIR="/opt/rpi-rgb-led-matrix"

if [ -d "$MATRIX_DIR" ]; then
    echo "RGB matrix library already installed at $MATRIX_DIR"
    read -p "Reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$MATRIX_DIR"
    else
        echo "Skipping library installation."
    fi
fi

if [ ! -d "$MATRIX_DIR" ]; then
    echo "Cloning rpi-rgb-led-matrix library..."
    sudo git clone https://github.com/hzeller/rpi-rgb-led-matrix.git "$MATRIX_DIR"

    echo "Building library..."
    cd "$MATRIX_DIR"
    sudo make

    echo "Building Python bindings..."
    cd "$MATRIX_DIR/bindings/python"
    sudo make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)
fi

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "To run the clock:"
echo "  sudo python3 clock.py"
echo ""
echo "To run in simulation mode (no hardware):"
echo "  python3 clock.py --simulate"
echo ""
echo "For help with options:"
echo "  python3 clock.py --help"
echo ""
