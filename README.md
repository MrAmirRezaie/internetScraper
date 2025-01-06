# Internet Scraper

    This script is designed to scrape data from various platforms such as Telegram, Twitter, Instagram, Facebook, and Google. The scraped data can be saved in multiple formats, including TXT, CSV, JSON, HTML, Excel, and SQLite database. The script is optimized to run on both desktop and mobile devices.

## Features

    - Scrape data from Telegram, Twitter, Instagram, Facebook, and Google.
    - Save data in TXT, CSV, JSON, HTML, Excel, and SQLite database formats.
    - Secure admin environment for generating and managing admin keys and codes.
    - Multi-stage encryption for protecting sensitive information.
    - Optimized for mobile devices with mobile user agent and window size settings.

## Security
    - Admin keys and codes are encrypted using multi-stage encryption (AES, DES3, Blowfish).
    - The script will self-destruct if admin keys or codes are missing or invalid.

## Requirements

    - Python 3.x
    - pip (for installing required packages)
    - ChromeDriver (for Selenium)

## Installation
   
    1. **Clone or download the repository.**
        ```bash
            git clone https://github.com/MrAmirRezaie/internetScraper.git
            cd internetScraper
        ```
        
    2. **Install the required packages:**
        ```bash
            pip install -r requirements.txt
        ```
      
    3. **Download and configure ChromeDriver:**
        - Download the appropriate version of ChromeDriver
        - Place the `chromedriver` executable in a directory included in your system's `PATH` (e.g., `/usr/local/bin`).
   
    4. **Run the script:**
        ```bash
        python internetScraper.py
        ```
      
## Usage

    1. After running the script, you will be prompted to enter input parameters such as usernames, platforms, keywords, etc.
    2. If you want to access the admin menu, type `yes`.
    3. The scraped data will be saved in the selected formats

## Admin Environment
    To access the admin environment, run the `admin_environment.py` script:
        ```
            python admin_environment.py
        ```
    This environment allows you to generate and manage admin keys and codes.
        - Generate Admin Keys: Generate and save public and secret keys.
        - Generate Admin Code: Generate an admin code with multi-stage encryption.
        - Read Admin Code: Decrypt and display the admin code.

## Running on Mobile Devices
    The script is optimized to run on mobile devices by setting a mobile user agent and adjusting the window size. This ensures that the script can interact with mobile versions of the platforms

## Mobile User Agent
    The script uses the following mobile user agent to simulate a mobile device:
        ```
            Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1
        ```

## Window Size
    The script sets the window size to 375x812 pixels, which is the size of an iPhone X screen. This ensures that the script can interact with mobile-optimized web pages.

## License
    This project is licensed under the MIT License.
   
## Installer
    ```bash
        #!/bin/bash

        # This script installs the prerequisites for the Internet Scraper script.

        # Detect the Linux distribution
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
        else
            echo "Unsupported Linux distribution. Exiting..."
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
            *)
                echo "Unsupported Linux distribution. Exiting..."
                exit 1
                ;;
        esac

        # Install required Python packages
        echo "Installing required Python packages..."
        pip3 install -r requirements.txt

        # Download and install ChromeDriver
        echo "Downloading and installing ChromeDriver..."
        LATEST_CHROMEDRIVER=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
        wget -O chromedriver.zip https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER/chromedriver_linux64.zip
        unzip chromedriver.zip
        sudo mv chromedriver /usr/local/bin/
        rm chromedriver.zip

        # Set executable permissions for scripts
        echo "Setting executable permissions..."
        chmod +x internetScraper.py
        chmod +x admin_environment.py

        echo "Installation completed successfully!"
    ```

    `requirements.txt`
        This file lists all the Python packages required for the script to run.
        ```
            selenium
            openpyxl
            numpy
            pyswarm
            pandas-datareader
            matplotlib
            pycryptodome
            sqlite3
        ```
## How to Use
    1. **Clone the Repository:**
        ```bash
            git clone https://github.com/MrAmirRezaie/internetScraper.git
            cd internetScraper
        ```

    2. **Run the Installer:**
        ```bash
            bash installer.sh
        ```

    3. Access the Admin Environment (if needed):
        ```bash
            python admin_environment.py
        ```

## Notes

    - ChromeDriver: Ensure that the version of ChromeDriver matches the version of Chrome installed on your system. You can check your Chrome version by navigating to `chrome://settings/help` in your browser.
    - Cross-Distribution Support: The `installer.sh` script supports Debian-based (e.g., Ubuntu), Red Hat-based (e.g., Fedora, CentOS), and Arch-based (e.g., Manjaro) distributions.
    - Security: Always keep admin keys and codes secure. Use multi-stage encryption for sensitive data.

## Contact

    - For questions or feedback, please contact:
    - Name: Mr Amir Rezaie
    - Email: MrAmirRezaie70@gmail.com
    - Github: MrAmirRezaie

## Contributing

    - Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes

## **Enjoy using the Internet Scraper script! 🚀**
