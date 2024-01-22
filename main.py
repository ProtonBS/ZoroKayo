import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from telegram import Bot, ParseMode
from telegram.ext import Updater, CommandHandler
import time

# Replace '6404454444:AAGo8zi-jGfqrX46aPciyLiMU8-10kHRj2w' with your actual Telegram bot token
TELEGRAM_BOT_TOKEN = '6404454444:AAGo8zi-jGfqrX46aPciyLiMU8-10kHRj2w'
CHAT_ID = 1835982315  # Replace with your actual Telegram chat ID
WEBSITE_URL = 'https://kayoanime.com'

def start(update, context):
    update.message.reply_text("Bot is running!")

def check_website(context):
    response = requests.get(WEBSITE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    new_post_title_element = soup.find('h2', class_='post-title')
    google_drive_link_element = soup.find('a', class_='google-drive-link')

    if new_post_title_element and google_drive_link_element:
        new_post_title = new_post_title_element.text
        google_drive_link = google_drive_link_element['href']

        if not context.job.context.get('last_post_title') or context.job.context['last_post_title'] != new_post_title:
            context.job.context['last_post_title'] = new_post_title
            context.bot.send_message(CHAT_ID, f"New post: {new_post_title}\nGoogle Drive link: {google_drive_link}", parse_mode=ParseMode.MARKDOWN)
        else:
            print("No new post detected.")
    else:
        print("Error: Post title or Google Drive link not found in the HTML structure.")

def fetch_gdrive_link(update, context):
    if context.args:
        post_link = context.args[0]
        update.message.reply_text("Please wait while I fetch the Google Drive link. This may take a moment...")

        # Take a screenshot of the webpage
        screenshot_path = generate_screenshot(post_link)

        # Wait for some time before fetching the Google Drive link
        time.sleep(10)

        # Fetch the Google Drive link
        google_drive_link = fetch_google_drive_link(post_link)

        if google_drive_link:
            update.message.reply_text(f"Google Drive link from the provided post: {google_drive_link}", parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text("Failed to fetch the Google Drive link.")
    else:
        update.message.reply_text("Please provide a Kayoanime post link.")

def generate_screenshot(url):
    # Use headless mode for taking screenshots without displaying a browser window
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Initialize the Chrome webdriver
    driver = webdriver.Chrome(options=options)

    try:
        # Open the webpage
        driver.get(url)

        # Take a screenshot
        screenshot_path = '/path/to/your/screenshot.png'
        driver.save_screenshot(screenshot_path)

        return screenshot_path
    finally:
        # Close the webdriver
        driver.quit()

def fetch_google_drive_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    google_drive_link_element = soup.find('a', class_='button-download', string='1080p')
    if google_drive_link_element:
        return google_drive_link_element['href']
    else:
        return None

def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)

    # Add command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('fetchgdrive', fetch_gdrive_link, pass_args=True))

    # Set up job to check the website periodically (adjust the interval as needed)
    updater.job_queue.run_repeating(check_website, interval=3600, first=0, context={"last_post_title": None})

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
