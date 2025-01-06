import os
import json
import hashlib
import logging
from Crypto.Cipher import AES, DES3, Blowfish
from Crypto.Util.Padding import pad, unpad
import base64
import time
import csv
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openpyxl import Workbook
import numpy as np
import pyswarm as ps
import pandas_datareader as pdt
import matplotlib.pyplot as plt
import subprocess
import pkg_resources
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import pandas as pd
from Crypto.Random import get_random_bytes

# Load environment variables from .env file
load_dotenv()

# Logging configuration to track the script's execution and errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internet_scraper.log'),
        logging.StreamHandler()
    ]
)

# Paths and URLs for the script to use
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'C:/Path/To/chromedriver.exe')
TELEGRAM_WEB_URL = 'https://web.telegram.org/'
TWITTER_URL = 'https://twitter.com/'
INSTAGRAM_URL = 'https://www.instagram.com/'
FACEBOOK_URL = 'https://www.facebook.com/'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q='
output_folder = os.getenv('OUTPUT_FOLDER', 'C:/Path/To/Output')

# Security keys and base URL from environment variables
SEC_KEY = os.getenv('SEC_KEY')
PUB_KEY = os.getenv('PUB_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.example.com')

# Set random seed and plot style
np.random.seed(0)
plt.style.use('ggplot')

# List of required packages
required_packages = [
    'selenium',
    'openpyxl',
    'numpy',
    'pyswarm',
    'pandas-datareader',
    'matplotlib',
    'pycryptodome',
    'sqlite3',
    'python-dotenv',
    'pytesseract',
    'pandas',
    'Pillow'
]

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMIN_CODE_FILE = "admin_codes.json"

# Paths and files for admin keys and codes
ADMIN_KEYS_FILE = 'admin_keys.json'
ADMIN_CODES_FILE = 'admin_codes.json'

# Database configuration
DATABASE_FILE = 'internet_scraper.db'

# Encryption keys from environment variables
KEY1 = os.getenv('ENCRYPTION_KEY1', get_random_bytes(16))
KEY2 = os.getenv('ENCRYPTION_KEY2', get_random_bytes(24))
KEY3 = os.getenv('ENCRYPTION_KEY3', get_random_bytes(32))

def install_packages():
    """Install required packages if they are not already installed."""
    for package in required_packages:
        try:
            pkg_resources.require(package)
            logging.info(f"{package} is already installed.")
        except pkg_resources.DistributionNotFound:
            logging.info(f"{package} is not installed. Installing...")
            subprocess.check_call(['pip', 'install', package])
            logging.info(f"{package} has been installed.")

def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return None

def read_sql_file(file_path):
    """Read data from an SQL file."""
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            data[table_name] = rows
        conn.close()
        return data
    except Exception as e:
        logging.error(f"Error reading SQL file: {e}")
        return None

def read_text_file(file_path):
    """Read data from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except Exception as e:
        logging.error(f"Error reading text file: {e}")
        return None

def read_csv_file(file_path):
    """Read data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return None

def read_excel_file(file_path):
    """Read data from an Excel file."""
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return None

def read_json_file(file_path):
    """Read data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Error reading JSON file: {e}")
        return None

def process_file(file_path):
    """Process a file based on its extension."""
    if file_path.endswith('.sql'):
        return read_sql_file(file_path)
    elif file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.csv'):
        return read_csv_file(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return read_excel_file(file_path)
    elif file_path.endswith('.json'):
        return read_json_file(file_path)
    elif file_path.endswith('.png') or file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        return extract_text_from_image(file_path)
    else:
        logging.error(f"Unsupported file format: {file_path}")
        return None

def get_user_input():
    """Get user inputs for the search parameters."""
    try:
        usernames = input("Enter the usernames or IDs of the target users (comma-separated): ").strip().split(',')
        phone_number = input("Enter your phone number for Telegram login: ")
        platforms = input("Enter platforms to search (comma-separated, e.g., Telegram,Twitter,Instagram): ").strip().split(',')
        keywords = input("Enter keywords to filter results (comma-separated, leave blank for no filter): ").strip().split(',')
        start_date = input("Enter start date (YYYY-MM-DD, leave blank for no filter): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD, leave blank for no filter): ").strip()
        max_results = input("Enter maximum number of results per platform (leave blank for no limit): ").strip()
        max_results = int(max_results) if max_results else None
        save_formats = input("Enter formats to save (comma-separated, e.g., txt,csv,json,html,xlsx): ").strip().split(',')
        return usernames, phone_number, platforms, keywords, start_date, end_date, max_results, save_formats
    except Exception as e:
        logging.error(f"Error getting user input: {e}")
        raise

def setup_driver():
    """Set up and configure the Selenium WebDriver for mobile."""
    try:
        service = Service(CHROME_DRIVER_PATH)
        options = webdriver.ChromeOptions()

        # Set mobile user agent
        mobile_user_agent = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        )
        options.add_argument(f'user-agent={mobile_user_agent}')

        if os.getenv('HEADLESS', 'true').lower() == 'true':
            options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=service, options=options)

        # Set window size for mobile
        driver.set_window_size(375, 812)  # اندازه صفحه iPhone X
        return driver
    except Exception as e:
        logging.error(f"Error setting up WebDriver: {e}")
        raise

def login_to_telegram(driver, phone_number):
    """Log in to Telegram using the provided phone number."""
    try:
        driver.get(TELEGRAM_WEB_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Log in by phone Number"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Phone number"]'))
        ).send_keys(phone_number + Keys.RETURN)
        logging.info("Please enter the verification code.")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="chat-list"]'))
        )
        logging.info("Logged in to Telegram successfully.")
    except TimeoutException as e:
        logging.error(f"Error logging into Telegram: {e}")
        raise

def search_telegram(driver, username, keywords, start_date, end_date, max_results):
    """Search Telegram for messages from a specific user."""
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]'))
        )
        search_box.send_keys(username)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{username}")]'))
        ).click()
        messages = []
        last_height = driver.execute_script("return document.querySelector('.messages-container').scrollHeight")
        while True:
            driver.execute_script(
                "document.querySelector('.messages-container').scrollTo(0, document.querySelector('.messages-container').scrollHeight);")
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "message")]'))
            )
            message_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "message")]')
            for element in message_elements:
                try:
                    user = element.find_element(By.XPATH, './/div[@class="message-author"]').text
                    text = element.find_element(By.XPATH, './/div[@class="message-text"]').text
                    message_type = 'text' if text else 'media'
                    date = element.find_element(By.XPATH, './/div[@class="message-date"]').text
                    message_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    if start_date and end_date:
                        start = datetime.strptime(start_date, '%Y-%m-%d')
                        end = datetime.strptime(end_date, '%Y-%m-%d')
                        if not (start <= message_date <= end):
                            continue

                    if keywords:
                        if not any(keyword.lower() in text.lower() for keyword in keywords):
                            continue

                    messages.append({
                        'platform': 'Telegram',
                        'username': username,
                        'content': text,
                        'content_type': message_type,
                        'date': date,
                        'url': TELEGRAM_WEB_URL
                    })

                    if max_results and len(messages) >= max_results:
                        break

                except NoSuchElementException as e:
                    logging.warning(f"Error extracting message: {e}")

            if max_results and len(messages) >= max_results:
                break

            new_height = driver.execute_script("return document.querySelector('.messages-container').scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        logging.info(f"Extracted {len(messages)} messages from Telegram for user {username}.")
        return messages
    except TimeoutException as e:
        logging.error(f"Error searching Telegram for user {username}: {e}")
        raise

def search_twitter(username, keywords, start_date, end_date, max_results):
    """Search Twitter for tweets from a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{TWITTER_URL}{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
        )
        tweets = []
        tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        for element in tweet_elements:
            try:
                text = element.find_element(By.XPATH, './/div[@lang]').text
                date = element.find_element(By.XPATH, './/time').get_attribute('datetime')
                tweet_url = element.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute('href')
                tweet_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if not (start <= tweet_date <= end):
                        continue

                if keywords:
                    if not any(keyword.lower() in text.lower() for keyword in keywords):
                        continue

                tweets.append({
                    'platform': 'Twitter',
                    'username': username,
                    'content': text,
                    'content_type': 'tweet',
                    'date': date,
                    'url': tweet_url
                })

                if max_results and len(tweets) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting tweet: {e}")

        logging.info(f"Extracted {len(tweets)} tweets from Twitter for user {username}.")
        return tweets
    except Exception as e:
        logging.error(f"Error searching Twitter for user {username}: {e}")
        return []
    finally:
        driver.quit()

def search_instagram(username, keywords, start_date, end_date, max_results):
    """Search Instagram for posts from a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{INSTAGRAM_URL}{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//article//img'))
        )
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//article//img')
        for element in post_elements:
            try:
                image_url = element.get_attribute('src')
                caption = element.find_element(By.XPATH, './/img').get_attribute('alt')
                post_date = datetime.now()

                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if not (start <= post_date <= end):
                        continue

                if keywords:
                    if not any(keyword.lower() in caption.lower() for keyword in keywords):
                        continue

                posts.append({
                    'platform': 'Instagram',
                    'username': username,
                    'content': caption,
                    'content_type': 'image',
                    'date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"{INSTAGRAM_URL}{username}"
                })

                if max_results and len(posts) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting post: {e}")

        logging.info(f"Extracted {len(posts)} posts from Instagram for user {username}.")
        return posts
    except Exception as e:
        logging.error(f"Error searching Instagram for user {username}: {e}")
        return []
    finally:
        driver.quit()

def search_facebook(username, keywords, start_date, end_date, max_results):
    """Search Facebook for posts from a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{FACEBOOK_URL}{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="article"]'))
        )
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[@role="article"]')
        for element in post_elements:
            try:
                text = element.find_element(By.XPATH, './/div[@data-ad-preview="message"]').text
                post_date = datetime.now()

                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if not (start <= post_date <= end):
                        continue

                if keywords:
                    if not any(keyword.lower() in text.lower() for keyword in keywords):
                        continue

                posts.append({
                    'platform': 'Facebook',
                    'username': username,
                    'content': text,
                    'content_type': 'post',
                    'date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"{FACEBOOK_URL}{username}"
                })

                if max_results and len(posts) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting post: {e}")

        logging.info(f"Extracted {len(posts)} posts from Facebook for user {username}.")
        return posts
    except Exception as e:
        logging.error(f"Error searching Facebook for user {username}: {e}")
        return []
    finally:
        driver.quit()

def search_google(username, keywords, start_date, end_date, max_results):
    """Search Google for results related to a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{GOOGLE_SEARCH_URL}{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="g"]'))
        )
        results = []
        search_results = driver.find_elements(By.XPATH, '//div[@class="g"]')
        for result in search_results:
            try:
                title = result.find_element(By.XPATH, './/h3').text
                link = result.find_element(By.XPATH, './/a').get_attribute('href')
                result_date = datetime.now()

                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if not (start <= result_date <= end):
                        continue

                if keywords:
                    if not any(keyword.lower() in title.lower() for keyword in keywords):
                        continue

                results.append({
                    'platform': 'Google',
                    'username': username,
                    'content': title,
                    'content_type': 'search_result',
                    'date': result_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': link
                })

                if max_results and len(results) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting search result: {e}")

        logging.info(f"Extracted {len(results)} search results from Google for user {username}.")
        return results
    except Exception as e:
        logging.error(f"Error searching Google for user {username}: {e}")
        return []
    finally:
        driver.quit()

def save_to_database(data, username):
    """Save data to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                username TEXT,
                content TEXT,
                content_type TEXT,
                date TEXT,
                url TEXT
            )
        ''')

        # Insert data into the table using parameterized queries
        for item in data:
            cursor.execute('''
                INSERT INTO scraped_data (platform, username, content, content_type, date, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (item['platform'], item['username'], item['content'], item['content_type'], item['date'], item['url']))

        conn.commit()
        conn.close()
        logging.info(f"Data saved to database for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to database for user {username}: {e}")
        raise

def save_to_txt(data, username):
    """Save data to a text file."""
    try:
        user_folder = os.path.join(output_folder, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.txt"), 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"Platform: {item['platform']}\n")
                f.write(f"Username: {item['username']}\n")
                f.write(f"Content: {item['content']}\n")
                f.write(f"Type: {item['content_type']}\n")
                f.write(f"Date: {item['date']}\n")
                f.write(f"URL: {item['url']}\n")
                f.write("=" * 50 + "\n")
        logging.info(f"Data saved to text file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to text file for user {username}: {e}")
        raise

def save_to_csv(data, username):
    """Save data to a CSV file."""
    try:
        user_folder = os.path.join(output_folder, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.csv"), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Platform', 'Username', 'Content', 'Type', 'Date', 'URL'])
            for item in data:
                writer.writerow(
                    [item['platform'], item['username'], item['content'], item['content_type'], item['date'],
                     item['url']])
        logging.info(f"Data saved to CSV file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to CSV file for user {username}: {e}")
        raise

def save_to_json(data, username):
    """Save data to a JSON file."""
    try:
        user_folder = os.path.join(output_folder, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data saved to JSON file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to JSON file for user {username}: {e}")
        raise

def save_to_html(data, username):
    """Save data to an HTML file."""
    try:
        user_folder = os.path.join(output_folder, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.html"), 'w', encoding='utf-8') as f:
            f.write('<html><body>\n')
            f.write(f'<h1>Internet Data for {username}</h1>\n')
            f.write('<table border="1">\n')
            f.write(
                '<tr><th>Platform</th><th>Username</th><th>Content</th><th>Type</th><th>Date</th><th>URL</th></tr>\n')
            for item in data:
                f.write(
                    f'<tr><td>{item["platform"]}</td><td>{item["username"]}</td><td>{item["content"]}</td><td>{item["content_type"]}</td><td>{item["date"]}</td><td><a href="{item["url"]}">Link</a></td></tr>\n')
            f.write('</table>\n')
            f.write('</body></html>\n')
        logging.info(f"Data saved to HTML file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to HTML file for user {username}: {e}")
        raise

def save_to_excel(data, username):
    """Save data to an Excel file."""
    try:
        user_folder = os.path.join(output_folder, username)
        os.makedirs(user_folder, exist_ok=True)
        wb = Workbook()
        ws = wb.active
        ws.title = username
        ws.append(['Platform', 'Username', 'Content', 'Type', 'Date', 'URL'])
        for item in data:
            ws.append(
                [item['platform'], item['username'], item['content'], item['content_type'], item['date'], item['url']])
        wb.save(os.path.join(user_folder, f"{username}.xlsx"))
        logging.info(f"Data saved to Excel file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to Excel file for user {username}: {e}")
        raise

def encrypt_data(data, key):
    """Encrypt data using AES encryption."""
    try:
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv, ct
    except Exception as e:
        logging.error(f"Error encrypting data: {e}")
        raise

def decrypt_data(iv, ct, key):
    """Decrypt data using AES decryption."""
    try:
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except Exception as e:
        logging.error(f"Error decrypting data: {e}")
        raise

def multi_stage_encryption(data):
    """Encrypt data in 8 stages using different encryption protocols."""
    try:
        key1 = KEY1
        key2 = KEY2
        key3 = KEY3

        # Stage 1: AES
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv1 = base64.b64encode(cipher.iv).decode('utf-8')
        ct1 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 2: DES3
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct1.encode(), DES3.block_size))
        iv2 = base64.b64encode(cipher.iv).decode('utf-8')
        ct2 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 3: Blowfish
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct2.encode(), Blowfish.block_size))
        iv3 = base64.b64encode(cipher.iv).decode('utf-8')
        ct3 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 4: AES again
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct3.encode(), AES.block_size))
        iv4 = base64.b64encode(cipher.iv).decode('utf-8')
        ct4 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 5: DES3 again
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct4.encode(), DES3.block_size))
        iv5 = base64.b64encode(cipher.iv).decode('utf-8')
        ct5 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 6: Blowfish again
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct5.encode(), Blowfish.block_size))
        iv6 = base64.b64encode(cipher.iv).decode('utf-8')
        ct6 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 7: AES again
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct6.encode(), AES.block_size))
        iv7 = base64.b64encode(cipher.iv).decode('utf-8')
        ct7 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 8: DES3 again
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct7.encode(), DES3.block_size))
        iv8 = base64.b64encode(cipher.iv).decode('utf-8')
        ct8 = base64.b64encode(ct_bytes).decode('utf-8')

        return {
            'iv1': iv1, 'ct1': ct1,
            'iv2': iv2, 'ct2': ct2,
            'iv3': iv3, 'ct3': ct3,
            'iv4': iv4, 'ct4': ct4,
            'iv5': iv5, 'ct5': ct5,
            'iv6': iv6, 'ct6': ct6,
            'iv7': iv7, 'ct7': ct7,
            'iv8': iv8, 'ct8': ct8
        }
    except Exception as e:
        logging.error(f"Error in multi-stage encryption: {e}")
        raise

def multi_stage_decryption(encrypted_data):
    """Decrypt data in 8 stages using different encryption protocols."""
    try:
        key1 = KEY1
        key2 = KEY2
        key3 = KEY3

        # Stage 8: DES3
        iv = base64.b64decode(encrypted_data['iv8'])
        ct = base64.b64decode(encrypted_data['ct8'])
        cipher = DES3.new(key2, DES3.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), DES3.block_size)
        data = pt.decode('utf-8')

        # Stage 7: AES
        iv = base64.b64decode(encrypted_data['iv7'])
        ct = base64.b64decode(encrypted_data['ct7'])
        cipher = AES.new(key1, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        data = pt.decode('utf-8')

        # Stage 6: Blowfish
        iv = base64.b64decode(encrypted_data['iv6'])
        ct = base64.b64decode(encrypted_data['ct6'])
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), Blowfish.block_size)
        data = pt.decode('utf-8')

        # Stage 5: DES3
        iv = base64.b64decode(encrypted_data['iv5'])
        ct = base64.b64decode(encrypted_data['ct5'])
        cipher = DES3.new(key2, DES3.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), DES3.block_size)
        data = pt.decode('utf-8')

        # Stage 4: AES
        iv = base64.b64decode(encrypted_data['iv4'])
        ct = base64.b64decode(encrypted_data['ct4'])
        cipher = AES.new(key1, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        data = pt.decode('utf-8')

        # Stage 3: Blowfish
        iv = base64.b64decode(encrypted_data['iv3'])
        ct = base64.b64decode(encrypted_data['ct3'])
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), Blowfish.block_size)
        data = pt.decode('utf-8')

        # Stage 2: DES3
        iv = base64.b64decode(encrypted_data['iv2'])
        ct = base64.b64decode(encrypted_data['ct2'])
        cipher = DES3.new(key2, DES3.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), DES3.block_size)
        data = pt.decode('utf-8')

        # Stage 1: AES
        iv = base64.b64decode(encrypted_data['iv1'])
        ct = base64.b64decode(encrypted_data['ct1'])
        cipher = AES.new(key1, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        data = pt.decode('utf-8')

        return data
    except Exception as e:
        logging.error(f"Error in multi-stage decryption: {e}")
        raise

def check_api_keys(public_key, secret_key):
    """Check if the API keys are valid and exist in the database."""
    try:
        # Retrieve valid keys from environment variables
        valid_public_key = os.getenv('VALID_PUBLIC_KEY')
        valid_secret_key = os.getenv('VALID_SECRET_KEY')
        return public_key == valid_public_key and secret_key == valid_secret_key
    except Exception as e:
        logging.error(f"Error checking API keys: {e}")
        raise

def admin_authentication():
    """Authenticate the admin user."""
    try:
        admin_username = input("Enter admin username: ")
        admin_password = input("Enter admin password: ")
        valid_admin_username = os.getenv('ADMIN_USERNAME')
        valid_admin_password = os.getenv('ADMIN_PASSWORD')
        return admin_username == valid_admin_username and admin_password == valid_admin_password
    except Exception as e:
        logging.error(f"Error in admin authentication: {e}")
        raise

def generate_admin_code(username):
    """Generate an admin code with multi-stage encryption based on username."""
    try:
        admin_code = f"ADMIN_CODE_{username}"
        encrypted_code = multi_stage_encryption(admin_code)
        return encrypted_code
    except Exception as e:
        logging.error(f"Error generating admin code: {e}")
        raise

def save_admin_code_to_file(encrypted_code):
    """Save the encrypted admin code to a text file."""
    try:
        with open(ADMIN_CODE_FILE, 'w') as f:
            json.dump(encrypted_code, f)
        logging.info("Admin code saved to file.")
    except Exception as e:
        logging.error(f"Error saving admin code to file: {e}")
        raise

def read_admin_code_from_file():
    """Read the encrypted admin code from a text file."""
    try:
        with open(ADMIN_CODE_FILE, 'r') as f:
            encrypted_code = json.load(f)
        return encrypted_code
    except FileNotFoundError:
        logging.error("Admin code file not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading admin code from file: {e}")
        raise

def verify_code_format(encrypted_code, username):
    """Verify the format and integrity of the admin code based on username."""
    if not isinstance(encrypted_code, dict):
        return False

    # Check required fields
    required_fields = ['iv1', 'ct1', 'iv2', 'ct2', 'iv3', 'ct3', 'iv4', 'ct4', 'iv5', 'ct5', 'iv6', 'ct6', 'iv7', 'ct7',
                       'iv8', 'ct8']
    if not all(field in encrypted_code for field in required_fields):
        return False

    # Verify the decrypted code matches the expected format
    try:
        decrypted_code = multi_stage_decryption(encrypted_code)
        expected_code = f"ADMIN_CODE_{username}"
        return decrypted_code == expected_code
    except Exception as e:
        logging.error(f"Error verifying admin code: {e}")
        return False

def delete_client_files():
    """Delete client files if the code format is invalid."""
    try:
        if os.path.exists(ADMIN_CODE_FILE):
            os.remove(ADMIN_CODE_FILE)
            logging.info(f"Deleted file: {ADMIN_CODE_FILE}")

        if os.path.exists(__file__):
            os.remove(__file__)
            logging.info(f"Deleted file: {__file__}")

        logging.info("Client files deleted due to invalid code format.")
    except Exception as e:
        logging.error(f"Error deleting client files: {e}")

def admin_menu():
    """Display the admin menu and handle admin operations."""
    try:
        if not admin_authentication():
            print("Admin authentication failed. Exiting...")
            return

        print("Admin Menu:")
        print("1. Generate Admin Code")
        print("2. Read Admin Code")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter admin username: ")
            encrypted_code = generate_admin_code(username)
            save_admin_code_to_file(encrypted_code)
            print("Admin code generated and saved successfully.")
        elif choice == "2":
            username = input("Enter admin username: ")
            encrypted_code = read_admin_code_from_file()
            if encrypted_code:
                decrypted_code = multi_stage_decryption(encrypted_code)
                print(f"Decrypted Admin Code: {decrypted_code}")
            else:
                print("No admin code found.")
        else:
            print("Invalid choice.")
    except Exception as e:
        logging.error(f"Error in admin menu: {e}")
        raise

if __name__ == '__main__':
    try:
        # Install required packages
        install_packages()

        # Check if the user wants to access the admin menu
        access_admin_menu = input("Do you want to access the admin menu? (yes/no): ").strip().lower()
        if access_admin_menu == "yes":
            admin_menu()
            exit()

        # Get user inputs
        usernames, phone_number, platforms, keywords, start_date, end_date, max_results, save_formats = get_user_input()

        # Check API keys
        public_key = input("Enter your public key: ")
        secret_key = input("Enter your secret key: ")
        if not check_api_keys(public_key, secret_key):
            print("Invalid API keys. Exiting...")
            exit()

        # Verify admin code format
        encrypted_code = read_admin_code_from_file()
        if not encrypted_code or not verify_code_format(encrypted_code, usernames[0]):
            logging.error("Invalid admin code format. Deleting client files...")
            delete_client_files()
            exit()

        # Set up the driver
        driver = setup_driver()
        try:
            # Log in to Telegram
            login_to_telegram(driver, phone_number)

            # Search and save data for each user
            for username in usernames:
                all_data = []
                if 'Telegram' in platforms:
                    all_data.extend(search_telegram(driver, username, keywords, start_date, end_date, max_results))
                if 'Twitter' in platforms:
                    all_data.extend(search_twitter(username, keywords, start_date, end_date, max_results))
                if 'Instagram' in platforms:
                    all_data.extend(search_instagram(username, keywords, start_date, end_date, max_results))
                if 'Facebook' in platforms:
                    all_data.extend(search_facebook(username, keywords, start_date, end_date, max_results))
                if 'Google' in platforms:
                    all_data.extend(search_google(username, keywords, start_date, end_date, max_results))

                # Save data in selected formats
                if 'txt' in save_formats:
                    save_to_txt(all_data, username)
                if 'csv' in save_formats:
                    save_to_csv(all_data, username)
                if 'json' in save_formats:
                    save_to_json(all_data, username)
                if 'html' in save_formats:
                    save_to_html(all_data, username)
                if 'xlsx' in save_formats:
                    save_to_excel(all_data, username)
                if 'db' in save_formats:
                    save_to_database(all_data, username)
        finally:
            # Close the driver
            driver.quit()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")