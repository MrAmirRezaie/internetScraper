#!/bin/bash

# Installer for Linux and macOS

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 not found. Please install Python 3."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "pip not found. Please install pip."
    exit 1
fi

# Create necessary directories
INSTALL_DIR="/usr/local/bin/internetScraper"
OUTPUT_DIR="/usr/local/share/internetScraper/output"
mkdir -p "$INSTALL_DIR"
mkdir -p "$OUTPUT_DIR"

# Copy script files
cp internetScraper.py "$INSTALL_DIR/"
cp .env "$INSTALL_DIR/"
cp -r output/* "$OUTPUT_DIR/"

# Install required packages
echo "Installing required packages..."

# List of required packages
REQUIRED_PACKAGES=(
    "selenium"
    "openpyxl"
    "numpy"
    "pandas"
    "matplotlib"
    "seaborn"
    "sqlalchemy"
    "beautifulsoup4"
    "nltk"
    "pycryptodome"
    "python-dotenv"
    "Pillow"
    "requests"
    "pyTelegramBotAPI"
    "googletrans==4.0.0-rc1"
    "cryptography"
    "tensorflow"
)

# Install each package
for package in "${REQUIRED_PACKAGES[@]}"; do
    echo "Installing $package..."
    pip3 install "$package"
    if [ $? -ne 0 ]; then
        echo "Failed to install $package"
        exit 1
    fi
done

# Create a symbolic link for easy access
ln -s "$INSTALL_DIR/internetScraper.py" /usr/local/bin/internetScraper

# Set executable permissions
chmod +x "$INSTALL_DIR/internetScraper.py"

echo "Installation completed successfully!"
echo "You can now run the script using the command 'internetScraper'."