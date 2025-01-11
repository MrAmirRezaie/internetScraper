import os
import json
import logging
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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from PIL import Image
from Crypto.Random import get_random_bytes
import argparse
import itertools
import string
from collections import defaultdict
import subprocess
import sqlite3
import importlib.metadata
import requests
import telebot
from googletrans import Translator
from cryptography.fernet import Fernet
import tensorflow as tf
from tensorflow.keras import layers, models

# Check if .env file exists, if not, create it with a new encryption key
if not os.path.exists('.env'):
    with open('.env', 'w') as env_file:
        encryption_key = Fernet.generate_key().decode()
        env_file.write(f"ENCRYPTION_KEY={encryption_key}\n")
    logging.info(".env file created with a new encryption key.")

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

# Telegram bot token and API URL
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/'

# Paths and URLs
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'chromedriver.exe')
TELEGRAM_WEB_URL = 'https://web.telegram.org/'
TWITTER_URL = 'https://twitter.com/'
INSTAGRAM_URL = 'https://www.instagram.com/'
FACEBOOK_URL = 'https://www.facebook.com/'
LINKEDIN_URL = 'https://www.linkedin.com/'
REDDIT_URL = 'https://www.reddit.com/'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q='
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')

# Security keys and base URL
SEC_KEY = None
PUB_KEY = None
BASE_URL = TELEGRAM_API_URL

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
    'Pillow',
    'requests',
    'pyTelegramBotAPI',
    'googletrans==4.0.0-rc1',
    'cryptography',
    'tensorflow'
]

# Database configuration
DATABASE_FILE = 'internet_scraper.db'
TELEGRAM_LINKS_DATABASE = 'telegram_links.db'

# Encryption keys
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    logging.error("ENCRYPTION_KEY not found in .env file. Exiting...")
    exit()
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

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

class AdminKey(Base):
    __tablename__ = 'admin_keys'
    id = Column(Integer, primary_key=True)
    pub_key = Column(String, unique=True)
    sec_key = Column(String, unique=True)
    expiry_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

Base.metadata.create_all(engine)

def encrypt_data(data):
    """Encrypt data using Fernet symmetric encryption."""
    if isinstance(data, str):
        data = data.encode()
    return cipher_suite.encrypt(data).decode()

def decrypt_data(encrypted_data):
    """Decrypt data using Fernet symmetric encryption."""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

def add_user(username, password, is_admin=False, expiry_days=30):
    """Add a new user to the database with encrypted password."""
    try:
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        password_hash = encrypt_data(password)
        user = User(
            username=username,
            password_hash=password_hash,
            is_admin=is_admin,
            expiry_date=expiry_date
        )
        session.add(user)
        session.commit()
        logging.info(f"User {username} added successfully.")
    except Exception as e:
        logging.error(f"Error adding user {username}: {e}")
        session.rollback()

def delete_expired_users():
    """Delete users whose expiry date has passed."""
    try:
        expired_users = session.query(User).filter(User.expiry_date < datetime.now()).all()
        for user in expired_users:
            session.delete(user)
        session.commit()
        logging.info(f"Deleted {len(expired_users)} expired users.")
    except Exception as e:
        logging.error(f"Error deleting expired users: {e}")
        session.rollback()

def check_user_credentials(username, password):
    """Check if the provided username and password are valid."""
    try:
        user = session.query(User).filter(User.username == username).first()
        if user and decrypt_data(user.password_hash) == password:
            if user.expiry_date > datetime.now():
                logging.info(f"User {username} authenticated successfully.")
                return True
            else:
                logging.warning(f"User {username} has expired.")
                delete_expired_users()
                return False
        else:
            logging.warning(f"Invalid credentials for user {username}.")
            return False
    except Exception as e:
        logging.error(f"Error checking credentials for user {username}: {e}")
        return False

def install_packages():
    """Install required packages."""
    for package in REQUIRED_PACKAGES:
        try:
            importlib.metadata.distribution(package)
            logging.info(f"{package} is already installed.")
        except importlib.metadata.PackageNotFoundError:
            logging.info(f"{package} is not installed. Installing...")
            subprocess.check_call(['pip', 'install', package])
            logging.info(f"{package} has been installed.")
        except Exception as e:
            logging.error(f"Error installing {package}: {e}")

def get_keys_from_telegram():
    """Get PUB_KEY and SEC_KEY from Telegram bot."""
    global SEC_KEY, PUB_KEY
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Please send your PUBLIC KEY.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        global SEC_KEY, PUB_KEY
        if not PUB_KEY:
            PUB_KEY = message.text
            bot.reply_to(message, "Please send your SECRET KEY.")
        elif not SEC_KEY:
            SEC_KEY = message.text
            bot.reply_to(message, "Keys received. You can now use the scraper.")
            bot.stop_polling()

    try:
        bot.polling()
    except Exception as e:
        logging.error(f"Error in Telegram bot polling: {e}")
        raise

def build_custom_ocr_model():
    """Build a custom OCR model using TensorFlow."""
    input_image = layers.Input(shape=(64, 128, 1), name='input_image')
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_image)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)
    output = layers.Dense(10 * 62, activation='softmax')(x)
    output = layers.Reshape((10, 62))(output)
    model = models.Model(inputs=input_image, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def extract_text_with_custom_ocr(image_path, model):
    """Extract text from an image using a custom OCR model."""
    try:
        img = Image.open(image_path).convert('L')
        img = img.resize((128, 64))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=-1)
        img = np.expand_dims(img, axis=0)
        prediction = model.predict(img)
        text = decode_prediction(prediction)
        return text
    except Exception as e:
        logging.error(f"Error extracting text with custom OCR: {e}")
        return None

def decode_prediction(prediction):
    """Decode the prediction from the custom OCR model."""
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = ""
    for i in range(prediction.shape[1]):
        text += characters[np.argmax(prediction[0, i])]
    return text

def translate_text(text, src_lang='auto', dest_lang='en'):
    """Translate text from one language to another using Google Translate."""
    try:
        translator = Translator()
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        logging.error(f"Error translating text: {e}")
        return None

def process_file(file_path, lang='eng', translate=False, dest_lang='en'):
    """Process a file based on its extension with OCR and translation support."""
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
        model = build_custom_ocr_model()
        text = extract_text_with_custom_ocr(file_path, model)
        if translate:
            text = translate_text(text, dest_lang=dest_lang)
        return text
    else:
        logging.error(f"Unsupported file format: {file_path}")
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

def search_linkedin(username, keywords, start_date, end_date, max_results):
    """Search LinkedIn for posts from a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{LINKEDIN_URL}in/{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]'))
        )
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]')
        for element in post_elements:
            try:
                text = element.find_element(By.XPATH, './/div[contains(@class, "feed-shared-update-v2__description")]').text
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
                    'platform': 'LinkedIn',
                    'username': username,
                    'content': text,
                    'content_type': 'post',
                    'date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"{LINKEDIN_URL}in/{username}",
                    'interaction_user': username
                })

                if max_results and len(posts) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting post: {e}")

        logging.info(f"Extracted {len(posts)} posts from LinkedIn for user {username}.")
        return posts
    except Exception as e:
        logging.error(f"Error searching LinkedIn for user {username}: {e}")
        return []
    finally:
        driver.quit()

def search_reddit(username, keywords, start_date, end_date, max_results):
    """Search Reddit for posts from a specific user."""
    try:
        driver = setup_driver()
        driver.get(f"{REDDIT_URL}user/{username}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Post")]'))
        )
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "Post")]')
        for element in post_elements:
            try:
                text = element.find_element(By.XPATH, './/h3[contains(@class, "PostTitle")]').text
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
                    'platform': 'Reddit',
                    'username': username,
                    'content': text,
                    'content_type': 'post',
                    'date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f"{REDDIT_URL}user/{username}",
                    'interaction_user': username
                })

                if max_results and len(posts) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting post: {e}")

        logging.info(f"Extracted {len(posts)} posts from Reddit for user {username}.")
        return posts
    except Exception as e:
        logging.error(f"Error searching Reddit for user {username}: {e}")
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
    parser.add_argument('--ocr_lang', type=str, default='eng', help='Language for OCR (e.g., eng, fas, ara, chi_sim)')
    parser.add_argument('--translate', action='store_true', help='Enable translation of extracted text')
    parser.add_argument('--dest_lang', type=str, default='en', help='Destination language for translation (e.g., en, fa, ar, zh-cn)')
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
        ocr_lang = args.ocr_lang
        translate = args.translate
        dest_lang = args.dest_lang

        proxies = get_proxies(proxy_input) if proxy_input else []

        # Get PUB_KEY and SEC_KEY from Telegram bot
        get_keys_from_telegram()

        username = input("Enter your username: ")

        # Check if API keys are provided
        if not PUB_KEY or not SEC_KEY:
            logging.error("Public key or secret key is missing. Exiting...")
            exit()

        # Validate API keys
        if not check_api_keys(PUB_KEY, SEC_KEY, username):
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
                platforms = ['Telegram', 'Twitter', 'Instagram', 'Facebook', 'LinkedIn', 'Reddit', 'Google']
                if 'Telegram' in platforms:
                    all_data.extend(search_telegram(driver, username, keywords, start_date, end_date, max_results))
                if 'Twitter' in platforms:
                    all_data.extend(search_twitter(username, keywords, start_date, end_date, max_results))
                if 'Instagram' in platforms:
                    all_data.extend(search_instagram(username, keywords, start_date, end_date, max_results))
                if 'Facebook' in platforms:
                    all_data.extend(search_facebook(username, keywords, start_date, end_date, max_results))
                if 'LinkedIn' in platforms:
                    all_data.extend(search_linkedin(username, keywords, start_date, end_date, max_results))
                if 'Reddit' in platforms:
                    all_data.extend(search_reddit(username, keywords, start_date, end_date, max_results))
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