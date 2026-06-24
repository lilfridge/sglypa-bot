import telebot
import markovify
import random
import threading
import time
import json
import os
from PIL import Image, ImageDraw, ImageFont
import io

TOKEN = "8464842453:AAE4QiUoCGhNdjNyCA3vRLMuloDOIinMPGc"
bot = telebot.TeleBot(TOKEN)

# Хранилище сообщений чата
messages_file = "messages.json"

def load_messages():
    if os.path.exists(messages_file):
        with open(messages_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_message(text):
    msgs = load_messages()
    msgs.append(text)
    if len(msgs) > 5000:
        msgs = msgs[-5000:]
    with open(messages_file, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False)

def generate_markov():
    msgs = load_messages()
    if len(msgs) < 10:
        return "ещё мало сообщений, пишите больше!"
    text = " ".join(msgs)
    try:
        model = markovify.Text(text, state_size=2)
        result = model.make_sentence(tries=50)
        return result if result else random.choice(msgs)
    except:
        return random.choice(msgs)

# Читаем все сообщения в чате
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    if message.text and not message.text.startswith('/'):
        save_message(message.text)
    
    # Отвечаем когда тегают
    if message.text and f'@{bot.get_me().username}' in message.text:
        reply = generate_markov()
        bot.reply_to(message, reply)

# Команда /сглыпа — генерирует сообщение
@bot.message_handler(commands=['sglypa', 'сглыпа'])
def cmd_sglypa(message):
    bot.send_message(message.chat.id, generate_markov())

# Мем — подпись к фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.caption and 'мем' in message.caption.lower():
        phrases = [
            "я так и знал", "ну и дела", "это нормально?",
            "жизнь боль", "хз что это но окей", "когда в 3 ночи",
            "братан ты видел это", "не ожидал такого поворота",
            "это я каждое утро", "ну привет"
        ]
        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        img = Image.open(io.BytesIO(downloaded)).convert("RGB")
        
        # Рисуем подпись
        draw = ImageDraw.Draw(img)
        w, h = img.size
        text = random.choice(phrases)
        draw.rectangle([0, h-50, w, h], fill=(0,0,0))
        draw.text((10, h-40), text, fill=(255,255,255))
        
        # Отправляем
        output = io.BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        bot.send_photo(message.chat.id, output)

# Случайные сообщения каждые 30-60 минут
def random_messages():
    while True:
        time.sleep(random.randint(1800, 3600))
        # Получи chat_id своей беседы и вставь сюда
        # bot.send_message(-100XXXXXXXXX, generate_markov())

threading.Thread(target=random_messages, daemon=True).start()

print("Бот запущен!")
bot.polling()

