import telebot
from datetime import datetime, timedelta
import pytz

API_TOKEN = '7415862022:AAEvrljMTbCNODKkMjIPgP-CTnIue9fwahQ'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пожалуйста, укажи свой часовой пояс в формате UTC, например, +3 или -5.")

@bot.message_handler(func=lambda message: True)
def get_timezone(message):
    try:
        user_timezone = int(message.text)
        if user_timezone < -12 or user_timezone > 14:
            raise ValueError("Invalid timezone offset")
        user_time = datetime.utcnow() + timedelta(hours=user_timezone)
        bot.reply_to(message, f"Ваше локальное время: {user_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError:
        bot.reply_to(message, "Неверный формат часового пояса. Пожалуйста, укажите часовой пояс в формате UTC, например, +3 или -5.")

bot.polling()