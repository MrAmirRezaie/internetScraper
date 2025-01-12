#!/bin/bash

# Internet Scraper Universal Installer for Linux
# Supports Debian-based (Ubuntu), Red Hat-based (Fedora, CentOS), and Arch-based distributions.

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install dependencies based on distribution
install_dependencies() {
    echo "Installing dependencies..."
    if command_exists apt; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv wget unzip
    elif command_exists dnf; then
        sudo dnf install -y python3 python3-pip python3-virtualenv wget unzip
    elif command_exists pacman; then
        sudo pacman -Syu --noconfirm python python-pip python-virtualenv wget unzip
    else
        echo "Unsupported package manager. Please install Python 3 and pip manually."
        exit 1
    fi
}

# Create virtual environment for the project
setup_virtualenv() {
    echo "Setting up a virtual environment..."
    python3 -m venv env
    source env/bin/activate
    echo "Virtual environment activated."
}

# Install required Python packages
install_python_packages() {
    echo "Installing required Python packages..."
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

    for package in "${REQUIRED_PACKAGES[@]}"; do
        pip install "$package"
        if [ $? -ne 0 ]; then
            echo "Failed to install $package. Exiting."
            exit 1
        fi
    done
    echo "All Python packages installed successfully."
}

# Set up directories and files
setup_directories() {
    echo "Setting up directories..."
    INSTALL_DIR="$HOME/internetScraper"
    OUTPUT_DIR="$INSTALL_DIR/output"

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$OUTPUT_DIR"

    cp internetScraper.py "$INSTALL_DIR/"
    cp .env "$INSTALL_DIR/"

    echo "Directories and files set up successfully."
}

# Create a symbolic link for the script
create_symlink() {
    echo "Creating symbolic link for easy access..."
    ln -sf "$INSTALL_DIR/internetScraper.py" "$HOME/.local/bin/internetScraper"
    chmod +x "$INSTALL_DIR/internetScraper.py"
    echo "You can now run the script using 'internetScraper'."
}

# Main installation process
main() {
    echo "Starting Internet Scraper installation..."

    # Check and install dependencies
    install_dependencies

    # Set up virtual environment
    setup_virtualenv

    # Install Python packages
    install_python_packages

    # Set up project directories and files
    setup_directories

    # Create a symbolic link for the script
    create_symlink

    echo "Installation completed successfully! 🎉"
    echo "Run 'source env/bin/activate' to activate the virtual environment."
    echo "Then use 'internetScraper' to start the script."
}

main
