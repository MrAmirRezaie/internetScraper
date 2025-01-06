# Internet Scraper and Admin Environment

This project consists of two main components: an **Internet Scraper** and an **Admin Environment**. The Internet Scraper is a powerful tool designed to scrape data from various social media platforms and save it in multiple formats, while the Admin Environment provides tools for generating and verifying admin codes using multi-stage encryption. This README provides a comprehensive guide on how to set up, configure, and use both components, along with detailed explanations of their features, security measures, and troubleshooting steps.

## Table of Contents
1. [Internet Scraper](#internet-scraper)
   - [Overview](#overview)
   - [Features](#features)
   - [Usage](#usage)
   - [Supported Platforms](#supported-platforms)
   - [Output Formats](#output-formats)
   - [Encryption](#encryption)
   - [Database Integration](#database-integration)
   - [OCR Support](#ocr-support)
   - [User Input and Filtering](#user-input-and-filtering)
   - [Headless Mode](#headless-mode)
   - [Error Handling](#error-handling)
   - [Advanced Features](#advanced-features)
   - [Performance Optimization](#performance-optimization)
   - [Customization](#customization)
   - [Data Validation](#data-validation)
2. [Admin Environment](#admin-environment)
   - [Overview](#overview-1)
   - [Features](#features-1)
   - [Usage](#usage-1)
   - [Multi-Stage Encryption](#multi-stage-encryption)
   - [Admin Code Management](#admin-code-management)
   - [Admin Menu](#admin-menu)
   - [Security Measures](#security-measures)
   - [Backup and Recovery](#backup-and-recovery)
   - [Audit Logging](#audit-logging)
   - [Access Control](#access-control)
3. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Setting Up the Project](#setting-up-the-project)
   - [Installing Dependencies](#installing-dependencies)
   - [Setting Up ChromeDriver](#setting-up-chromedriver)
   - [Setting Up Tesseract OCR](#setting-up-tesseract-ocr)
   - [Setting Up Proxy](#setting-up-proxy)
   - [Setting Up Virtual Environment](#setting-up-virtual-environment)
4. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
   - [Output Folder Configuration](#output-folder-configuration)
   - [Database Configuration](#database-configuration)
   - [Encryption Keys](#encryption-keys)
   - [Proxy Configuration](#proxy-configuration)
   - [Custom User Agents](#custom-user-agents)
   - [Custom Scripts](#custom-scripts)
5. [Logging](#logging)
   - [Log Files](#log-files)
   - [Log Levels](#log-levels)
   - [Log Format](#log-format)
   - [Debugging with Logs](#debugging-with-logs)
   - [Log Rotation](#log-rotation)
   - [Audit Logging](#audit-logging-1)
6. [Security](#security)
   - [API Key Validation](#api-key-validation)
   - [Encryption](#encryption-1)
   - [Environment Variables](#environment-variables-1)
   - [Admin Code Security](#admin-code-security)
   - [Data Privacy](#data-privacy)
   - [Network Security](#network-security)
   - [Access Control](#access-control-1)
   - [Data Integrity](#data-integrity)
7. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [Debugging Tips](#debugging-tips)
   - [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
8. [License](#license)
9. [Contributing](#contributing)
10. [Contact](#contact)

---

## Internet Scraper

### Overview
The Internet Scraper is a Python-based tool that allows users to scrape data from popular social media platforms such as Telegram, Twitter, Instagram, Facebook, and Google. It provides advanced filtering options, supports multiple output formats, and ensures data security through encryption. The tool is designed to be user-friendly, with an interactive command-line interface for input and configuration.

### Features
- **Platform Support**: Scrape data from Telegram, Twitter, Instagram, Facebook, and Google.
- **Filtering Options**: Filter results by keywords, date range, and maximum number of results.
- **Output Formats**: Save scraped data in TXT, CSV, JSON, HTML, Excel (XLSX), and SQLite database formats.
- **Encryption**: Secure sensitive data using multi-stage encryption (AES, DES3, Blowfish).
- **Database Integration**: Store scraped data in an SQLite database for easy querying and analysis.
- **OCR Support**: Extract text from images using Optical Character Recognition (OCR).
- **User Input**: Interactive command-line interface for user input.
- **Headless Mode**: Run the scraper in headless mode for automation.
- **Error Handling**: Robust error handling and logging for debugging.
- **Advanced Features**: Support for multi-threading, custom user agents, and proxy integration.
- **Performance Optimization**: Optimized for high performance with minimal resource usage.
- **Customization**: Highly customizable with support for custom scripts and plugins.
- **Data Validation**: Validate scraped data to ensure accuracy and completeness.

### Usage
1. Run the `internetScraper.py` script.
2. Enter the usernames or IDs of the target users (comma-separated).
3. Provide your phone number for Telegram login.
4. Select the platforms to search (e.g., Telegram, Twitter, Instagram).
5. Optionally, enter keywords to filter results and specify a date range.
6. Choose the output formats for saving the data (e.g., TXT, CSV, JSON).
7. The script will scrape the data and save it in the specified formats.

### Supported Platforms
- **Telegram**: Scrape messages from specific users or groups.
- **Twitter**: Extract tweets from a user's profile.
- **Instagram**: Scrape posts and captions from a user's profile.
- **Facebook**: Extract posts from a user's timeline.
- **Google**: Search for results related to a specific user.

### Output Formats
- **TXT**: Plain text file with structured data.
- **CSV**: Comma-separated values file for easy import into spreadsheets.
- **JSON**: Structured data in JSON format for programmatic use.
- **HTML**: Web page with a table displaying the scraped data.
- **Excel (XLSX)**: Excel file for data analysis.
- **SQLite Database**: Store data in a local SQLite database for querying.

### Encryption
The Internet Scraper uses multi-stage encryption to secure sensitive data such as admin codes and API keys. The encryption process involves three algorithms:
- **AES (Advanced Encryption Standard)**
- **DES3 (Triple Data Encryption Standard)**
- **Blowfish**

Each stage of encryption adds an additional layer of security, making it difficult for unauthorized users to decrypt the data.

### Database Integration
The scraped data can be saved in an SQLite database (`internet_scraper.db`). The database schema includes the following fields:
- `id`: Unique identifier for each record.
- `platform`: The platform from which the data was scraped.
- `username`: The username or ID of the target user.
- `content`: The content of the scraped data (e.g., message, tweet, post).
- `content_type`: The type of content (e.g., text, image, tweet).
- `date`: The date and time of the scraped data.
- `url`: The URL of the scraped content.

### OCR Support
The Internet Scraper includes support for Optical Character Recognition (OCR) using the `pytesseract` library. This allows the tool to extract text from images, which can be useful for scraping data from platforms that use images to display text.

### User Input and Filtering
The tool provides an interactive command-line interface for user input. Users can specify:
- **Usernames**: Comma-separated list of usernames or IDs to scrape.
- **Platforms**: Comma-separated list of platforms to search (e.g., Telegram, Twitter).
- **Keywords**: Comma-separated list of keywords to filter results.
- **Date Range**: Start and end dates to filter results by date.
- **Maximum Results**: Maximum number of results to scrape per platform.

### Headless Mode
The Internet Scraper can run in headless mode, which allows it to operate without a graphical user interface (GUI). This is useful for automation and running the script on servers or in environments where a GUI is not available.

### Error Handling
The script includes robust error handling to ensure that it can recover from unexpected issues. Errors are logged to the `internet_scraper.log` file, which can be used for debugging.

### Advanced Features
- **Multi-Threading**: The scraper supports multi-threading to speed up data collection.
- **Custom User Agents**: Users can specify custom user agents to mimic different devices or browsers.
- **Proxy Integration**: The scraper can be configured to use proxies for anonymous scraping.
- **Dynamic Content Handling**: The scraper can handle dynamically loaded content using Selenium.
- **Custom Scripts**: Users can add custom scripts to extend the functionality of the scraper.

### Performance Optimization
The Internet Scraper is optimized for high performance with minimal resource usage. It uses efficient algorithms and data structures to ensure fast and reliable data scraping.

### Customization
The Internet Scraper is highly customizable, allowing users to add custom scripts, plugins, and configurations to meet their specific needs.

### Data Validation
The scraper includes data validation mechanisms to ensure that the scraped data is accurate and complete. This includes checks for missing data, invalid formats, and inconsistencies.

---

## Admin Environment

### Overview
The Admin Environment is a Python-based tool designed to generate and verify admin codes using multi-stage encryption. It provides a secure way to manage admin access and ensure the integrity of the system.

### Features
- **Admin Code Generation**: Generate encrypted admin codes using multi-stage encryption.
- **Admin Code Verification**: Verify the integrity of admin codes.
- **File Management**: Save and load encrypted admin codes from files.
- **Admin Menu**: Interactive command-line interface for admin operations.
- **Security Measures**: Multi-stage encryption and secure storage of admin codes.
- **Backup and Recovery**: Backup and recovery options for admin codes.
- **Audit Logging**: Log all admin activities for auditing purposes.
- **Access Control**: Restrict access to sensitive operations using admin codes.

### Usage
1. Run the `admin_environment.py` script.
2. Choose to generate or verify an admin code.
   - **Generate Admin Code**: Enter the admin username, and the script will generate and save the encrypted admin code.
   - **Verify Admin Code**: Enter the admin username, and the script will verify the encrypted admin code.
3. The script will display the results of the operation.

### Multi-Stage Encryption
The Admin Environment uses the same multi-stage encryption process as the Internet Scraper. The encryption process involves three algorithms:
- **AES (Advanced Encryption Standard)**
- **DES3 (Triple Data Encryption Standard)**
- **Blowfish**

Each stage of encryption adds an additional layer of security, ensuring that admin codes are securely stored and transmitted.

### Admin Code Management
Admin codes are saved in a JSON file (`admin_codes.json`). The file contains the encrypted admin code along with the initialization vectors (IVs) for each stage of encryption. The Admin Environment provides functions to:
- **Generate Admin Codes**: Create a new admin code and save it to the file.
- **Verify Admin Codes**: Decrypt and verify the admin code against the expected format.
- **Load Admin Codes**: Load the encrypted admin code from the file for verification.

### Admin Menu
The Admin Environment includes an interactive menu for managing admin codes. The menu options include:
- **Generate Admin Code**: Generate a new admin code and save it to the file.
- **Verify Admin Code**: Verify the integrity of an existing admin code.

### Security Measures
- **Multi-Stage Encryption**: Admin codes are encrypted using AES, DES3, and Blowfish.
- **Secure Storage**: Encrypted admin codes are stored in a JSON file with restricted access.
- **Environment Variables**: Sensitive information such as encryption keys are stored in environment variables.

### Backup and Recovery
The Admin Environment includes options for backing up and recovering admin codes. Backups are stored in a secure location and can be restored in case of data loss.

### Audit Logging
All admin activities are logged for auditing purposes. The logs include details such as the admin username, action performed, and timestamp.

### Access Control
Access to the Admin Environment is restricted to authorized users. Admin codes are required to perform sensitive operations.

---

## Installation

### Prerequisites
- Python 3.7 or higher.
- Chrome browser installed.
- ChromeDriver matching your Chrome browser version.
- Tesseract OCR installed (for OCR support).
- Proxy server (optional, for anonymous scraping).

### Setting Up the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/internet-scraper.git
   ```

2. Navigate to the project directory:
   ```bash
   cd internet-scraper
   ```

3. Install the required packages using the following command:
   ```bash
   pip install -r requirements.txt
   ```

### Setting Up ChromeDriver
- Ensure that the ChromeDriver executable is correctly configured and matches your Chrome browser version. Download the correct version.

### Setting Up Tesseract OCR
- Install Tesseract OCR on your system and ensure that it is accessible from the command line. On Windows, you may need to add the Tesseract installation directory to your system's `PATH`.

### Setting Up Proxy
- To use a proxy, set the following environment variables:
  ```plaintext
  HTTP_PROXY=http://your-proxy:port
  HTTPS_PROXY=https://your-proxy:port
  ```

### Setting Up Virtual Environment
- To create a virtual environment, run the following commands:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
  pip install -r requirements.txt
  ```
  
## Configuration

### Environment Variables
- Create a `.env` file in the project root directory and add the following environment variables:
  ```plaintext
  CHROME_DRIVER_PATH=C:/Path/To/chromedriver.exe
  OUTPUT_FOLDER=C:/Path/To/Output
  SEC_KEY=your_secret_key
  PUB_KEY=your_public_key
  BASE_URL=https://api.example.com
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD=admin123
  VALID_PUBLIC_KEY=your_valid_public_key
  VALID_SECRET_KEY=your_valid_secret_key
  ENCRYPTION_KEY1=your_encryption_key1
  ENCRYPTION_KEY2=your_encryption_key2
  ENCRYPTION_KEY3=your_encryption_key3
  ```

### Output Folder Configuration
- The `OUTPUT_FOLDER` environment variable specifies the directory where the scraped data will be saved. Ensure that the folder exists and is writable.

### Database Configuration
- The SQLite database (`internet_scraper.db`) is automatically created if it does not exist. The database schema is defined in the script and includes fields for platform, username, content, content type, date, and URL.

### Encryption Keys
- The encryption keys (`ENCRYPTION_KEY1`, `ENCRYPTION_KEY2`, `ENCRYPTION_KEY3`) are used for multi-stage encryption. These keys should be kept secure and not shared.

### Proxy Configuration
- To use a proxy, set the following environment variables:
  ```bash
  HTTP_PROXY=http://your-proxy:port
  HTTPS_PROXY=https://your-proxy:port
  ```

### Custom User Agents
- To use custom user agents, modify the `setup_driver()` function in the `internetScraper.py` script to include the desired user agent string.

### Custom Scripts
- Users can add custom `scripts` to extend the functionality of the scraper. These scripts can be placed in the scripts directory and imported as needed.

## Logging

### Log Files

1. Both scripts log their activities to respective log files:
   - `internet_scraper.log` for the Internet Scraper.
   - `admin_environment.log` for the Admin Environment.

### Log Levels

2. Logs include timestamps, log levels, and messages to help track the execution and debug issues. The log levels are:
   - **INFO**: General information about the script's execution.
   - **WARNING**: Non-critical issues that may affect functionality.
   - **ERROR**: Critical errors that prevent the script from functioning.

### Log Format

3. The log format is as follows:
   ```
   [timestamp] [log level] - [message]
   ```

### Debugging with Logs

4. Logs are the primary tool for debugging issues. Check the log files for detailed error messages and stack traces.

### Log Rotation

5. Log rotation is not implemented by default. For long-running scripts, consider using a logging library that supports log rotation.

### Audit Logging

6. All admin activities are logged for auditing purposes. The logs include details such as the admin username, action performed, and timestamp.

## Security

### API Key Validation
- The script checks the validity of API keys before proceeding with data scraping. Invalid keys will result in the script terminating.

### Encryption
- Sensitive data such as admin codes and API keys are encrypted using multi-stage encryption (AES, DES3, Blowfish). This ensures that even if the data is intercepted, it cannot be easily decrypted.

### Environment Variables
- Sensitive information such as API keys and encryption keys are stored in environment variables for added security. This prevents hardcoding sensitive data in the script.

### Admin Code Security
- Admin codes are encrypted using multi-stage encryption and stored in a JSON file. The encryption process ensures that the codes cannot be easily decrypted without the correct keys.

### Data Privacy
- The Internet Scraper is designed to respect user privacy and only scrape publicly available data. It does not attempt to bypass any platform's security measures.

### Network Security
- The script can be configured to use HTTPS for secure communication with external APIs. Ensure that all API endpoints use HTTPS to prevent data interception.

### Access Control
- Access to the Admin Environment is restricted to authorized users. Admin codes are required to perform sensitive operations.

### Data Integrity
- The scraper includes mechanisms to ensure data integrity, such as checksums and data validation.

## Troubleshooting
1. Common Issues
   - **ChromeDriver Issues**: Ensure that the ChromeDriver executable matches your Chrome browser version.
   - **Missing Packages**: Run `pip install -r requirements.txt` to install all required packages.
   - **Log Files**: Check the log files (`internet_scraper.log` and `admin_environment.log`) for detailed error messages.

2. Debugging Tips
   - Run the script in non-headless mode to see the browser actions.
   - Check the log files for detailed error messages.
   - Ensure that all environment variables are correctly set in the `.env` file.

3. Frequently Asked Questions (FAQ)
   - **Q: How do I update ChromeDriver?**
         - A: Download the latest version of ChromeDriver from the official website and replace the existing executable.
   - **Q: Can I scrape data from private accounts?**
         - A: No, the scraper can only access publicly available data.
   - **Q: How do I change the output folder?**
         - A: Update the `OUTPUT_FOLDER` environment variable in the `.env` file.

## License
   - This project is licensed under the MIT License.

## Contributing
   - Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes

## Contact

   - For questions or feedback, please contact:
   - Name: Mr Amir Rezaie
   - Email: MrAmirRezaie70@gmail.com
   - Github: MrAmirRezaie

## **Enjoy using the Internet Scraper script! 🚀**
