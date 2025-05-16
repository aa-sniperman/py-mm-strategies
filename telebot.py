import telebot
from settings import settings

WHITELISTED_CHAT_IDS = [5455613873, 1484119212, 7661814523]

bot = telebot.TeleBot(settings.telegram.bot_token)

def send_message(msg: str):
    for user_id in WHITELISTED_CHAT_IDS:
        try:
            bot.send_message(user_id, msg)
        except Exception as err:
            print(f"Failed to send message to {user_id}: {err}")









