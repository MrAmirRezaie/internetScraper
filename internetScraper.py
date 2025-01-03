import time
import csv
import json
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openpyxl import Workbook

logging.basicConfig(
    filename='internet_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CHROME_DRIVER_PATH = 'C:/Path/To/chromedriver.exe'
TELEGRAM_WEB_URL = 'https://web.telegram.org/'
TWITTER_URL = 'https://twitter.com/'
INSTAGRAM_URL = 'https://www.instagram.com/'
FACEBOOK_URL = 'https://www.facebook.com/'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q='
output_folder = 'C:/Path/To/Output'

def get_user_input():
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

def setup_driver():
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_telegram(driver, phone_number):
    try:
        driver.get(TELEGRAM_WEB_URL)
        time.sleep(5)
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Log in by phone Number"]'))
        )
        login_button.click()
        time.sleep(2)
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Phone number"]'))
        )
        phone_input.send_keys(phone_number)
        phone_input.send_keys(Keys.RETURN)
        time.sleep(2)
        logging.info("Please enter the verification code.")
        time.sleep(20)
        logging.info("Logged in to Telegram successfully.")
    except TimeoutException as e:
        logging.error(f"Error logging into Telegram: {e}")
        raise

def search_telegram(driver, username, keywords, start_date, end_date, max_results):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]'))
        )
        search_box.send_keys(username)
        time.sleep(2)
        user_chat = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{username}")]'))
        )
        user_chat.click()
        time.sleep(5)
        messages = []
        last_height = driver.execute_script("return document.querySelector('.messages-container').scrollHeight")
        while True:
            driver.execute_script("document.querySelector('.messages-container').scrollTo(0, document.querySelector('.messages-container').scrollHeight);")
            time.sleep(2)
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
    try:
        driver = setup_driver()
        driver.get(f"{TWITTER_URL}{username}")
        time.sleep(5)
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
    try:
        driver = setup_driver()
        driver.get(f"{INSTAGRAM_URL}{username}")
        time.sleep(5)
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
    try:
        driver = setup_driver()
        driver.get(f"{FACEBOOK_URL}{username}")
        time.sleep(5)
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
    try:
        driver = setup_driver()
        driver.get(f"{GOOGLE_SEARCH_URL}{username}")
        time.sleep(5)
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

def save_to_txt(data, username):
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

def save_to_csv(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    with open(os.path.join(user_folder, f"{username}.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Platform', 'Username', 'Content', 'Type', 'Date', 'URL'])
        for item in data:
            writer.writerow([item['platform'], item['username'], item['content'], item['content_type'], item['date'], item['url']])

def save_to_json(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    with open(os.path.join(user_folder, f"{username}.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_html(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    with open(os.path.join(user_folder, f"{username}.html"), 'w', encoding='utf-8') as f:
        f.write('<html><body>\n')
        f.write(f'<h1>Internet Data for {username}</h1>\n')
        f.write('<table border="1">\n')
        f.write('<tr><th>Platform</th><th>Username</th><th>Content</th><th>Type</th><th>Date</th><th>URL</th></tr>\n')
        for item in data:
            f.write(f'<tr><td>{item["platform"]}</td><td>{item["username"]}</td><td>{item["content"]}</td><td>{item["content_type"]}</td><td>{item["date"]}</td><td><a href="{item["url"]}">Link</a></td></tr>\n')
        f.write('</table>\n')
        f.write('</body></html>\n')

def save_to_excel(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = username
    ws.append(['Platform', 'Username', 'Content', 'Type', 'Date', 'URL'])
    for item in data:
        ws.append([item['platform'], item['username'], item['content'], item['content_type'], item['date'], item['url']])
    wb.save(os.path.join(user_folder, f"{username}.xlsx"))

if __name__ == '__main__':
    usernames, phone_number, platforms, keywords, start_date, end_date, max_results, save_formats = get_user_input()
    driver = setup_driver()
    try:
        login_to_telegram(driver, phone_number)
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
    finally:
        driver.quit()