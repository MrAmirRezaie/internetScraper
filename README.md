# Internet Scraper

This Python script is designed to scrape data from various social media platforms and Google search results based on user input. It uses Selenium for web automation and supports multiple output formats for saving the scraped data.

## Features

- **Platforms Supported**: Telegram, Twitter, Instagram, Facebook, and Google.
- **Output Formats**: TXT, CSV, JSON, HTML, and Excel (XLSX).
- **Filtering Options**: Keywords, date range, and maximum number of results.
- **Logging**: Detailed logging for debugging and tracking the scraping process.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Selenium (`pip install selenium`)
- OpenPyXL (`pip install openpyxl`)
- ChromeDriver (Ensure the path to ChromeDriver is correctly set in the script)

## Configuration

1. **ChromeDriver Path**: Update the `CHROME_DRIVER_PATH` variable in the script with the correct path to your ChromeDriver executable.
2. **Output Folder**: Set the `output_folder` variable to the desired directory where the scraped data will be saved.

## Usage

1. **Run the Script**: Execute the script using Python.
2. **Input Parameters**:
   - **Usernames or IDs**: Enter the usernames or IDs of the target users, separated by commas.
   - **Phone Number**: Enter your phone number for Telegram login.
   - **Platforms**: Specify the platforms to search (e.g., Telegram, Twitter, Instagram), separated by commas.
   - **Keywords**: Enter keywords to filter the results, separated by commas. Leave blank for no filter.
   - **Date Range**: Enter the start and end dates in `YYYY-MM-DD` format. Leave blank for no date filter.
   - **Maximum Results**: Enter the maximum number of results to retrieve per platform. Leave blank for no limit.
   - **Save Formats**: Specify the formats to save the data (e.g., txt, csv, json, html, xlsx), separated by commas.

## Functions

- **`get_user_input()`**: Prompts the user for input parameters.
- **`setup_driver()`**: Initializes and configures the Chrome WebDriver.
- **`login_to_telegram()`**: Logs into Telegram using the provided phone number.
- **`search_telegram()`**: Searches for messages in Telegram based on the provided username and filters.
- **`search_twitter()`**: Searches for tweets on Twitter based on the provided username and filters.
- **`search_instagram()`**: Searches for posts on Instagram based on the provided username and filters.
- **`search_facebook()`**: Searches for posts on Facebook based on the provided username and filters.
- **`search_google()`**: Searches for results on Google based on the provided username and filters.
- **`save_to_txt()`**: Saves the scraped data to a TXT file.
- **`save_to_csv()`**: Saves the scraped data to a CSV file.
- **`save_to_json()`**: Saves the scraped data to a JSON file.
- **`save_to_html()`**: Saves the scraped data to an HTML file.
- **`save_to_excel()`**: Saves the scraped data to an Excel file.

## Example

```bash
$ python internet_scraper.py
Enter the usernames or IDs of the target users (comma-separated): user1,user2
Enter your phone number for Telegram login: +1234567890
Enter platforms to search (comma-separated, e.g., Telegram,Twitter,Instagram): Telegram,Twitter
Enter keywords to filter results (comma-separated, leave blank for no filter): python,selenium
Enter start date (YYYY-MM-DD, leave blank for no filter): 2023-01-01
Enter end date (YYYY-MM-DD, leave blank for no filter): 2023-12-31
Enter maximum number of results per platform (leave blank for no limit): 10
Enter formats to save (comma-separated, e.g., txt,csv,json,html,xlsx): txt,csv
