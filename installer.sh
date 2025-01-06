#!/bin/bash

# This script installs the prerequisites for the Internet Scraper script.

# Detect the operating system
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
elif [ -f /etc/debian_version ]; then
    OS=debian
elif [ -f /etc/redhat-release ]; then
    OS=rhel
elif [ -f /etc/arch-release ]; then
    OS=arch
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS=macos
elif [[ "$OSTYPE" == "android"* ]]; then
    OS=android
else
    echo "Unsupported operating system. Exiting..."
    exit 1
fi

# Update the system and install prerequisites
echo "Updating the system and installing prerequisites..."
case $OS in
    debian|ubuntu)
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip git wget unzip
        ;;
    fedora|rhel|centos)
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip git wget unzip
        ;;
    arch|manjaro)
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm python python-pip git wget unzip
        ;;
    macos)
        if ! command -v brew &> /dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3 git wget unzip
        ;;
    android)
        if ! command -v pkg &> /dev/null; then
            echo "Termux is required for Android. Please install Termux from the Play Store."
            exit 1
        fi
        pkg update -y
        pkg install -y python git wget unzip
        ;;
    *)
        echo "Unsupported operating system. Exiting..."
        exit 1
        ;;
esac

# Install required Python packages
echo "Installing required Python packages..."
pip3 install -r requirements.txt

# Download and install ChromeDriver (only for desktop systems)
if [[ "$OS" != "android" ]]; then
    echo "Downloading and installing ChromeDriver..."
    LATEST_CHROMEDRIVER=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
    wget -O chromedriver.zip https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER/chromedriver_linux64.zip
    unzip chromedriver.zip
    sudo mv chromedriver /usr/local/bin/
    rm chromedriver.zip
fi

# Set executable permissions for scripts
echo "Setting executable permissions..."
chmod +x internetScraper.py
chmod +x admin_environment.py

echo "Installation completed successfully!"
