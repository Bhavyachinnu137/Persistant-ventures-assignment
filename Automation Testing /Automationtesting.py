import telebot
import requests
import logging
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize Telegram Bot
bot = telebot.TeleBot('7536808477:AAFn46jVQ1FyTdVVQIiTABUqODXmp5Ft7jE')

# API Endpoints to Monitor
api_endpoints = {
    "Telegram API": f"https://api.telegram.org/bot{bot.token}/getUpdates",
    "Google Play Store App": "https://play.google.com/store/apps/details?id=com.facesearch.app&hl=en-US",
    "Apple App Store App": "https://apps.apple.com/in/app/face-search-ai-pimeyes/id6504996249"
}

# Global variable to control background monitoring
stop_monitoring = threading.Event()

# Function to Monitor APIs
def monitor_apis():
    status_report = {}
    for name, url in api_endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status_report[name] = "Online"
            else:
                status_report[name] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            status_report[name] = f"Failed: {str(e)}"
    return status_report

# Telegram Command to Start Interaction
@bot.message_handler(commands=['start'])
def start(message):
    menu_message = (
        "Welcome! Please choose what you would like to check:\n"
        "1. Check API Statuses\n"
        "2. Start Background Monitoring\n"
        "3. Stop Background Monitoring\n"
        "Send the number corresponding to your choice."
    )
    bot.send_message(message.chat.id, menu_message, parse_mode='html')

# Handle user input for menu choices
@bot.message_handler(func=lambda message: message.text in ['1', '2', '3'])
def handle_choice(message):
    global stop_monitoring

    if message.text == '1':
        bot.send_message(message.chat.id, "Checking app statuses... Please wait.", parse_mode='html')
        status_report = monitor_apis()
        response_message = "Application Status Report:\n"
        for app, status in status_report.items():
            response_message += f"{app}: {status}\n"
        bot.send_message(message.chat.id, response_message, parse_mode='html')

    elif message.text == '2':
        if not stop_monitoring.is_set():
            stop_monitoring.clear()
            bot.send_message(message.chat.id, "Starting background monitoring...", parse_mode='html')
            monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
            monitoring_thread.start()
        else:
            bot.send_message(message.chat.id, "Background monitoring is already running.", parse_mode='html')

    elif message.text == '3':
        if not stop_monitoring.is_set():
            stop_monitoring.set()
            bot.send_message(message.chat.id, "Stopping background monitoring...", parse_mode='html')
        else:
            bot.send_message(message.chat.id, "Background monitoring is not running.", parse_mode='html')

# Function to Continuously Monitor APIs and Send Alerts
def background_monitoring():
    last_status = {}
    while not stop_monitoring.is_set():
        current_status = monitor_apis()
        for app, status in current_status.items():
            if app not in last_status or last_status[app] != status:
                alert_message = f"ALERT: {app} status changed to {status}"
                bot.send_message(7041517630, alert_message)  # Replace with your chat ID
        last_status = current_status
        time.sleep(60)  # Monitor every 60 seconds
    logging.info("Background monitoring process stopped.")

# Start Polling
if __name__ == "__main__":
    try:
        # Start bot polling
        bot.infinity_polling(none_stop=True)
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
        stop_monitoring.set()
