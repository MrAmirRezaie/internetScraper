import os
import json
import hashlib
import logging
from Crypto.Cipher import AES, DES3, Blowfish
from Crypto.Util.Padding import pad, unpad
import base64
import time
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openpyxl import Workbook
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import pytesseract
from PIL import Image
from Crypto.Random import get_random_bytes
import argparse
import itertools
import string
from collections import defaultdict
import subprocess
import sqlite3
import pkg_resources
import requests

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internet_scraper.log'),
        logging.StreamHandler()
    ]
)

# Paths and URLs
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'chromedriver.exe')
TELEGRAM_WEB_URL = 'https://web.telegram.org/'
TWITTER_URL = 'https://twitter.com/'
INSTAGRAM_URL = 'https://www.instagram.com/'
FACEBOOK_URL = 'https://www.facebook.com/'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q='
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')

# Security keys and base URL
SEC_KEY = os.getenv('SEC_KEY', 'default_secret_key')
PUB_KEY = os.getenv('PUB_KEY', 'default_public_key')
BASE_URL = os.getenv('BASE_URL', 'https://mramirrezaie.ir/api.php')

# Set random seed and plot style
np.random.seed(0)
plt.style.use('ggplot')

# Required packages
REQUIRED_PACKAGES = [
    'selenium',
    'openpyxl',
    'numpy',
    'pandas',
    'matplotlib',
    'seaborn',
    'sqlalchemy',
    'beautifulsoup4',
    'nltk',
    'pycryptodome',
    'python-dotenv',
    'pytesseract',
    'Pillow',
    'requests'
]

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMIN_CODE_FILE = "admin_codes.json"
ADMIN_KEYS_FILE = 'admin_keys.json'
ADMIN_CODES_FILE = 'admin_codes.json'

# Database configuration
DATABASE_FILE = 'internet_scraper.db'
TELEGRAM_LINKS_DATABASE = 'telegram_links.db'

# Encryption keys
KEY1 = os.getenv('ENCRYPTION_KEY1', get_random_bytes(16))
KEY2 = os.getenv('ENCRYPTION_KEY2', get_random_bytes(24))
KEY3 = os.getenv('ENCRYPTION_KEY3', get_random_bytes(32))

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(f'sqlite:///{DATABASE_FILE}')
Session = sessionmaker(bind=engine)
session = Session()

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    platform = Column(String)
    username = Column(String)
    content = Column(String)
    content_type = Column(String)
    date = Column(DateTime)
    url = Column(String)
    interaction_user = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    expiry_date = Column(DateTime)

Base.metadata.create_all(engine)

def install_packages():
    """Install required packages."""
    for package in REQUIRED_PACKAGES:
        try:
            pkg_resources.require(package)
            logging.info(f"{package} is already installed.")
        except pkg_resources.DistributionNotFound:
            logging.info(f"{package} is not installed. Installing...")
            subprocess.check_call(['pip', 'install', package])
            logging.info(f"{package} has been installed.")
        except Exception as e:
            logging.error(f"Error installing {package}: {e}")

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

def read_proxy_list(file_path):
    """Read a list of proxies from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            proxies = f.read().splitlines()
        return proxies
    except Exception as e:
        logging.error(f"Error reading proxy list from file: {e}")
        return []

def setup_driver(proxy=None):
    """Set up and configure the Selenium WebDriver."""
    try:
        service = Service(CHROME_DRIVER_PATH)
        options = webdriver.ChromeOptions()

        mobile_user_agent = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        )
        options.add_argument(f'user-agent={mobile_user_agent}')

        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        if os.getenv('HEADLESS', 'true').lower() == 'true':
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=service, options=options)

        driver.set_window_size(375, 812)
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
                        'url': TELEGRAM_WEB_URL,
                        'interaction_user': user
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
                    'url': tweet_url,
                    'interaction_user': username
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
                    'url': f"{INSTAGRAM_URL}{username}",
                    'interaction_user': username
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
                    'url': f"{FACEBOOK_URL}{username}",
                    'interaction_user': username
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
                    'url': link,
                    'interaction_user': username
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
        for item in data:
            scraped_data = ScrapedData(
                platform=item['platform'],
                username=item['username'],
                content=item['content'],
                content_type=item['content_type'],
                date=datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S'),
                url=item['url'],
                interaction_user=item.get('interaction_user', '')
            )
            session.add(scraped_data)
        session.commit()
        logging.info(f"Data saved to database for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to database for user {username}: {e}")
        raise

def save_to_txt(data, username):
    """Save data to a text file."""
    try:
        user_folder = os.path.join(OUTPUT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.txt"), 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"Platform: {item['platform']}\n")
                f.write(f"Username: {item['username']}\n")
                f.write(f"Content: {item['content']}\n")
                f.write(f"Type: {item['content_type']}\n")
                f.write(f"Date: {item['date']}\n")
                f.write(f"URL: {item['url']}\n")
                f.write(f"Interaction User: {item.get('interaction_user', 'N/A')}\n")
                f.write("=" * 50 + "\n")
        logging.info(f"Data saved to text file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to text file for user {username}: {e}")
        raise

def save_to_csv(data, username):
    """Save data to a CSV file."""
    try:
        user_folder = os.path.join(OUTPUT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(user_folder, f"{username}.csv"), index=False)
        logging.info(f"Data saved to CSV file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to CSV file for user {username}: {e}")
        raise

def save_to_json(data, username):
    """Save data to a JSON file."""
    try:
        user_folder = os.path.join(OUTPUT_FOLDER, username)
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
        user_folder = os.path.join(OUTPUT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)
        with open(os.path.join(user_folder, f"{username}.html"), 'w', encoding='utf-8') as f:
            f.write('<html><body>\n')
            f.write(f'<h1>Internet Data for {username}</h1>\n')
            f.write('<table border="1">\n')
            f.write(
                '<tr><th>Platform</th><th>Username</th><th>Content</th><th>Type</th><th>Date</th><th>URL</th><th>Interaction User</th></tr>\n')
            for item in data:
                f.write(
                    f'<tr><td>{item["platform"]}</td><td>{item["username"]}</td><td>{item["content"]}</td><td>{item["content_type"]}</td><td>{item["date"]}</td><td><a href="{item["url"]}">Link</a></td><td>{item.get("interaction_user", "N/A")}</td></tr>\n')
            f.write('</table>\n')
            f.write('</body></html>\n')
        logging.info(f"Data saved to HTML file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to HTML file for user {username}: {e}")
        raise

def save_to_excel(data, username):
    """Save data to an Excel file."""
    try:
        user_folder = os.path.join(OUTPUT_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)
        df = pd.DataFrame(data)
        df.to_excel(os.path.join(user_folder, f"{username}.xlsx"), index=False)
        logging.info(f"Data saved to Excel file for user {username}.")
    except Exception as e:
        logging.error(f"Error saving data to Excel file for user {username}: {e}")
        raise

def visualize_data(data, username):
    """Visualize data using Matplotlib and Seaborn."""
    try:
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 6))
        sns.countplot(x='platform', data=df)
        plt.title(f"Data Distribution for {username}")
        plt.xlabel('Platform')
        plt.ylabel('Count')
        plt.savefig(os.path.join(OUTPUT_FOLDER, username, f"{username}_data_distribution.png"))
        plt.close()
        logging.info(f"Data visualization saved for user {username}.")
    except Exception as e:
        logging.error(f"Error visualizing data for user {username}: {e}")

def analyze_sentiment(text):
    """Analyze sentiment of the text using NLTK."""
    try:
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        return sentiment
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Internet Scraper')
    parser.add_argument('--usernames', type=str, help='Comma-separated list of usernames to search')
    parser.add_argument('--keywords', type=str, help='Comma-separated list of keywords to search')
    parser.add_argument('--start_date', type=str, help='Start date for search (YYYY-MM-DD)')
    parser.add_argument('--end_date', type=str, help='End date for search (YYYY-MM-DD)')
    parser.add_argument('--max_results', type=int, help='Maximum number of results to retrieve')
    parser.add_argument('--save_formats', type=str, help='Comma-separated list of formats to save data (txt, csv, json, html, xlsx, db)')
    parser.add_argument('--proxy', type=str, help='Proxy to use for scraping')
    return parser.parse_args()

def get_proxies(proxy_input):
    """Get a list of proxies from input or file."""
    if proxy_input.endswith('.txt'):
        return read_proxy_list(proxy_input)
    else:
        return [proxy_input]

def check_api_keys(public_key, secret_key, username):
    """Check if the provided API keys are valid by calling the API."""
    if not public_key or not secret_key or not username:
        logging.error("Public key, secret key, or username is missing.")
        return False

    try:
        response = requests.post(
            BASE_URL,
            json={'publicKey': public_key, 'secretKey': secret_key, 'username': username},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('message') == 'Keys are valid':
                logging.info("API keys and username are valid.")
                return True
            else:
                logging.error(f"API returned invalid message: {result.get('message')}")
                return False
        else:
            logging.error(f"API returned status code {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error validating API keys: {e}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding API response: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error validating API keys: {e}")
        return False

def read_admin_code_from_file():
    """Read the admin code from a file."""
    try:
        if not os.path.exists(ADMIN_CODE_FILE):
            logging.error("Admin code file not found.")
            return None
        with open(ADMIN_CODE_FILE, 'r') as f:
            encrypted_code = json.load(f)
        return encrypted_code
    except Exception as e:
        logging.error(f"Error reading admin code file: {e}")
        return None

def verify_code_format(code, username):
    """Verify the format of the admin code."""
    return code.startswith(username) and len(code) == 32

def delete_client_files():
    """Delete client files in case of invalid admin code."""
    try:
        if os.path.exists(ADMIN_CODE_FILE):
            os.remove(ADMIN_CODE_FILE)
        if os.path.exists(ADMIN_KEYS_FILE):
            os.remove(ADMIN_KEYS_FILE)
        if os.path.exists(ADMIN_CODES_FILE):
            os.remove(ADMIN_CODES_FILE)
        logging.info("Client files deleted due to invalid admin code.")
    except Exception as e:
        logging.error(f"Error deleting client files: {e}")

def validate_script_with_api(script_content):
    """Validate script using the API."""
    try:
        response = requests.post(
            BASE_URL,
            json={'script_content': script_content},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            return result['is_valid'], result.get('message', '')
        else:
            logging.error(f"API returned status code {response.status_code}: {response.text}")
            return False, "API validation failed."
    except Exception as e:
        logging.error(f"Error validating script with API: {e}")
        return False, "API validation failed."

def main():
    try:
        args = parse_arguments()

        install_packages()

        keywords = args.keywords.split(',') if args.keywords else []
        start_date = args.start_date
        end_date = args.end_date
        max_results = args.max_results
        save_formats = args.save_formats.split(',') if args.save_formats else []
        proxy_input = args.proxy

        proxies = get_proxies(proxy_input) if proxy_input else []

        public_key = input("Enter your public key: ")
        secret_key = input("Enter your secret key: ")
        username = input("Enter your username: ")

        # بررسی اینکه نام کاربری وارد شده است
        if not username:
            logging.error("Username is required. Exiting...")
            exit()

        # Check if API keys are provided
        if not public_key or not secret_key:
            logging.error("Public key or secret key is missing. Exiting...")
            exit()

        # Validate API keys
        if not check_api_keys(public_key, secret_key, username):
            logging.error("Invalid API keys or username. Exiting...")
            exit()

        encrypted_code = read_admin_code_from_file()
        if not encrypted_code or not verify_code_format(encrypted_code, username):
            logging.error("Invalid admin code format. Deleting client files...")
            delete_client_files()
            exit()

        for proxy in proxies:
            try:
                driver = setup_driver(proxy)
                phone_number = input("Enter your phone number for Telegram login: ")
                login_to_telegram(driver, phone_number)

                all_data = []
                platforms = ['Telegram', 'Twitter', 'Instagram', 'Facebook', 'Google']
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

                # Validate script using API
                for item in all_data:
                    is_valid, message = validate_script_with_api(item['content'])
                    if not is_valid:
                        logging.warning(f"Script validation failed for {username}: {message}")
                        if "expired" in message.lower():
                            delete_client_files()
                            exit()

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

                visualize_data(all_data, username)

            except Exception as e:
                logging.error(f"Error using proxy {proxy}: {e}")
            finally:
                driver.quit()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")

if __name__ == '__main__':
    main()