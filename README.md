# Internet Scraper 🚀

Welcome to the **Internet Scraper**! This powerful tool simplifies data scraping across multiple platforms while ensuring security, flexibility, and scalability. 🌐

---

## 📂 Project Structure

- **internetScraper.py**: The main script for web scraping, data analysis, and visualization.
- **installer.sh**: A universal shell script for setting up the environment on various Linux distributions.
- **installer.bat**: A batch script for Windows installation.
- **.env**: Configuration file for environment variables.
- **output/**: Directory where all scraped data will be saved.

---

## 🛠️ Installation

### For Linux:
This project is compatible with most Linux distributions, including Ubuntu, Fedora, CentOS, and Arch Linux.

1. Clone the repository:
   ```bash
   git clone https://github.com/MrAmirRezaie/internetScraper
   cd internet-scraper
   ```

2. Run the installer script:
   ```bash
   bash installer.sh
   ```

3. Activate the virtual environment:
   ```bash
   source env/bin/activate
   ```

4. Run the scraper:
   ```bash
   internetScraper
   ```

### For Windows:
1. Clone the repository and navigate to its directory.
2. Run the batch installer:
   ```cmd
   installer.bat
   ```
3. Use Python to run the script directly.

---

## 🔧 Command-Line Options

| Option          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `--usernames`    | Comma-separated list of usernames to scrape data for.                      |
| `--keywords`     | Comma-separated list of keywords to filter the data.                       |
| `--start_date`   | The start date for filtering data (YYYY-MM-DD).                            |
| `--end_date`     | The end date for filtering data (YYYY-MM-DD).                              |
| `--max_results`  | The maximum number of results to retrieve.                                 |
| `--save_formats` | Output formats for the data (txt, csv, json, html, xlsx, db).              |
| `--proxy`        | Proxy server to use during scraping.                                       |
| `--ocr_lang`     | Language for OCR processing (e.g., eng, fas, ara).                         |
| `--translate`    | Enable text translation (optional).                                        |
| `--dest_lang`    | Destination language for translation (default: en).                       |

### Example Usage:
```bash
python3 internetScraper.py --usernames "john_doe" --keywords "example" --start_date "2023-01-01" --end_date "2023-12-31" --max_results 50 --save_formats "csv,json"
```

---

## 📊 Features

### Platform Support:
The Internet Scraper supports the following platforms:
- **Telegram**: Extract messages, links, and user interactions.
- **Twitter**: Scrape tweets, mentions, hashtags, and metadata.
- **Instagram**: Collect captions, image metadata, and post details.
- **Facebook**: Retrieve posts, shared content, and user comments.
- **LinkedIn**: Extract professional posts and activities.
- **Reddit**: Scrape subreddit posts, comments, and votes.
- **Google**: Gather metadata from search results.

### Additional Features:
- **Data Export**: Save scraped data in various formats, including `.txt`, `.csv`, `.json`, `.html`, `.xlsx`, and SQLite database.
- **Visualization**: Use built-in visualizations to analyze data distribution and trends.
- **Text Translation**: Translate scraped text into over 100 languages.
- **Sentiment Analysis**: Use NLTK for analyzing the sentiment of text.
- **Custom OCR**: Extract text from images using a TensorFlow-based OCR model.

---

## 🔐 Security

We prioritize the security and privacy of your data:
- **Environment Variables**: Sensitive information, such as API keys, is stored securely in the `.env` file.
- **Encryption**: All data is encrypted using **Fernet** symmetric encryption to prevent unauthorized access.
- **Secure Storage**: Ensure your `.env` file and database are kept in secure locations.

---

## 💻 How It Works

1. **Setup and Initialization**:
   - Install the required dependencies and set up the virtual environment.
   - Configure the `.env` file with the necessary API keys and paths.

2. **Run the Script**:
   - Use the command-line options to specify usernames, keywords, date ranges, and output formats.

3. **Data Scraping**:
   - The scraper navigates through platforms using Selenium WebDriver.
   - Extracted data is processed, filtered, and stored securely.

4. **Export and Analysis**:
   - Data is saved in the specified formats and can be analyzed using visualizations or external tools.

---

## 📞 Contact

For questions, feedback, or bug reports, contact the maintainer:
- **Email**: MrAmirRezaie70@gmail.com
- **Telegram**: [@MrAmirRezaie](https://t.me/MrAmirRezaie)
- **GitHub**: [internetScraper](https://github.com/MrAmirRezaie/internetScraper)

---

## 📜 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute.

---

Happy Scraping! 😃