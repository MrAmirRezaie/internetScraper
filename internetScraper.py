import time
import csv
import json
import logging
import os
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from openpyxl import Workbook
from fpdf import FPDF
import xml.etree.ElementTree as ET

logging.basicConfig(
    filename='internet_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Determine the operating system
os_type = platform.system()

# Set driver paths based on the operating system
if os_type == "Windows":
    CHROME_DRIVER_PATH = 'C:/Path/To/chromedriver.exe'
    FIREFOX_DRIVER_PATH = 'C:/Path/To/geckodriver.exe'
    EDGE_DRIVER_PATH = 'C:/Path/To/msedgedriver.exe'
elif os_type == "Linux":
    CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
    FIREFOX_DRIVER_PATH = '/usr/local/bin/geckodriver'
    EDGE_DRIVER_PATH = '/usr/local/bin/msedgedriver'
elif os_type == "Darwin":  # macOS
    CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
    FIREFOX_DRIVER_PATH = '/usr/local/bin/geckodriver'
    EDGE_DRIVER_PATH = '/usr/local/bin/msedgedriver'
else:
    raise Exception("Unsupported operating system")

TELEGRAM_WEB_URL = 'https://web.telegram.org/'
TWITTER_URL = 'https://twitter.com/'
INSTAGRAM_URL = 'https://www.instagram.com/'
FACEBOOK_URL = 'https://www.facebook.com/'
LINKEDIN_URL = 'https://www.linkedin.com/'
REDDIT_URL = 'https://www.reddit.com/'
YOUTUBE_URL = 'https://www.youtube.com/'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q='
output_folder = os.path.join(os.path.expanduser('~'), 'InternetScraperOutput')

def get_user_input():
    usernames = input("Enter the usernames or IDs of the target users (comma-separated): ").strip().split(',')
    phone_number = input("Enter your phone number for Telegram login: ")
    platforms = input("Enter platforms to search (comma-separated, e.g., Telegram,Twitter,Instagram,LinkedIn,Reddit,YouTube): ").strip().split(',')
    keywords = input("Enter keywords to filter results (comma-separated, leave blank for no filter): ").strip().split(',')
    start_date = input("Enter start date (YYYY-MM-DD, leave blank for no filter): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD, leave blank for no filter): ").strip()
    max_results = input("Enter maximum number of results per platform (leave blank for no limit): ").strip()
    max_results = int(max_results) if max_results else None
    save_formats = input("Enter formats to save (comma-separated, e.g., txt,csv,json,html,xlsx,pdf,xml): ").strip().split(',')
    browser = input("Enter browser to use (chrome, firefox, edge): ").strip().lower()
    use_proxy = input("Use proxy? (yes/no): ").strip().lower() == 'yes'
    proxy = None
    if use_proxy:
        proxy = input("Enter proxy address (e.g., http://proxy.example.com:8080): ").strip()
    return usernames, phone_number, platforms, keywords, start_date, end_date, max_results, save_formats, browser, proxy

def setup_driver(browser, proxy=None):
    if browser == 'firefox':
        service = FirefoxService(FIREFOX_DRIVER_PATH)
        options = webdriver.FirefoxOptions()
        if proxy:
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.http', proxy)
            options.set_preference('network.proxy.http_port', 8080)
        driver = webdriver.Firefox(service=service, options=options)
    elif browser == 'edge':
        service = EdgeService(EDGE_DRIVER_PATH)
        options = webdriver.EdgeOptions()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Edge(service=service, options=options)
    else:
        service = ChromeService(CHROME_DRIVER_PATH)
        options = webdriver.ChromeOptions()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
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
        driver = setup_driver(browser)
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
        driver = setup_driver(browser)
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
        driver = setup_driver(browser)
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

def search_linkedin(username, keywords, start_date, end_date, max_results):
    try:
        driver = setup_driver(browser)
        driver.get(f"{LINKEDIN_URL}{username}")
        time.sleep(5)
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[@class="feed-shared-update-v2"]')
        for element in post_elements:
            try:
                text = element.find_element(By.XPATH, './/div[@class="feed-shared-update-v2__description"]').text
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
                    'url': f"{LINKEDIN_URL}{username}"
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
    try:
        driver = setup_driver(browser)
        driver.get(f"{REDDIT_URL}{username}")
        time.sleep(5)
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[@class="Post"]')
        for element in post_elements:
            try:
                text = element.find_element(By.XPATH, './/h3[@class="_eYtD2XCVieq6emjKBH3m"]').text
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
                    'url': f"{REDDIT_URL}{username}"
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

def search_youtube(username, keywords, start_date, end_date, max_results):
    try:
        driver = setup_driver(browser)
        driver.get(f"{YOUTUBE_URL}{username}")
        time.sleep(5)
        videos = []
        video_elements = driver.find_elements(By.XPATH, '//div[@id="dismissible"]')
        for element in video_elements:
            try:
                title = element.find_element(By.XPATH, './/a[@id="video-title"]').text
                video_url = element.find_element(By.XPATH, './/a[@id="video-title"]').get_attribute('href')
                video_date = datetime.now()

                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    if not (start <= video_date <= end):
                        continue

                if keywords:
                    if not any(keyword.lower() in title.lower() for keyword in keywords):
                        continue

                videos.append({
                    'platform': 'YouTube',
                    'username': username,
                    'content': title,
                    'content_type': 'video',
                    'date': video_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': video_url
                })

                if max_results and len(videos) >= max_results:
                    break

            except NoSuchElementException as e:
                logging.warning(f"Error extracting video: {e}")

        logging.info(f"Extracted {len(videos)} videos from YouTube for user {username}.")
        return videos
    except Exception as e:
        logging.error(f"Error searching YouTube for user {username}: {e}")
        return []
    finally:
        driver.quit()

def search_google(username, keywords, start_date, end_date, max_results):
    try:
        driver = setup_driver(browser)
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

def save_to_pdf(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for item in data:
        pdf.cell(200, 10, txt=f"Platform: {item['platform']}", ln=True)
        pdf.cell(200, 10, txt=f"Username: {item['username']}", ln=True)
        pdf.cell(200, 10, txt=f"Content: {item['content']}", ln=True)
        pdf.cell(200, 10, txt=f"Type: {item['content_type']}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {item['date']}", ln=True)
        pdf.cell(200, 10, txt=f"URL: {item['url']}", ln=True)
        pdf.cell(200, 10, txt="=" * 50, ln=True)
    pdf.output(os.path.join(user_folder, f"{username}.pdf"))

def save_to_xml(data, username):
    user_folder = os.path.join(output_folder, username)
    os.makedirs(user_folder, exist_ok=True)
    root = ET.Element("data")
    for item in data:
        entry = ET.SubElement(root, "entry")
        ET.SubElement(entry, "platform").text = item['platform']
        ET.SubElement(entry, "username").text = item['username']
        ET.SubElement(entry, "content").text = item['content']
        ET.SubElement(entry, "type").text = item['content_type']
        ET.SubElement(entry, "date").text = item['date']
        ET.SubElement(entry, "url").text = item['url']
    tree = ET.ElementTree(root)
    tree.write(os.path.join(user_folder, f"{username}.xml"), encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    usernames, phone_number, platforms, keywords, start_date, end_date, max_results, save_formats, browser, proxy = get_user_input()
    driver = setup_driver(browser, proxy)
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
            if 'LinkedIn' in platforms:
                all_data.extend(search_linkedin(username, keywords, start_date, end_date, max_results))
            if 'Reddit' in platforms:
                all_data.extend(search_reddit(username, keywords, start_date, end_date, max_results))
            if 'YouTube' in platforms:
                all_data.extend(search_youtube(username, keywords, start_date, end_date, max_results))
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
            if 'pdf' in save_formats:
                save_to_pdf(all_data, username)
            if 'xml' in save_formats:
                save_to_xml(all_data, username)
    finally:
        driver.quit()