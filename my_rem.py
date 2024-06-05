import telebot
import datetime
import time
import threading
import random
from openpyxl import load_workbook
from io import BytesIO

def check_time_fmt(shdl_time):
    if len(shdl_time) != 5:
        return False
    shdl_hh = int(shdl_time[0:2])
    shdl_ddot = shdl_time[2]
    shdl_min = int(shdl_time[3:5])
    if 0 <= shdl_hh < 24 and shdl_ddot == ':' and 0 <= shdl_min < 60:
        return True
    else: return False

topic = ["Пора на работу","Duolingo пока едешь", "Что нового в почте", "Можешь попить кофе",
           "Сколько задач остались?", "Иногда люди обедают", "Начадьник тебя видел?", "Составь план на завтра",
           "может уже домой?", "Зерокот что пишет?", "Домашку сделал?", "не стоит поздно ложиться спать"]
shedule = ["8:00","8:45","9:30","11:30","12:00","15:00","17:00","18:00","19:30","20:00","22:40","23:00"]

shift = "99:"
for i in range(20):
    shedule.append(shift + str(i+18))

bot = telebot.TeleBot('7394207851:AAFzbujyT1ekzK2I2OOOD95XXL7hK0KON9M')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message,"Привет! Я чат бот, который может напоминать учить уроки и делать домашку!"
                        "/shedule - задать новое расписание в чате\n"
                        "можно загрузить файл .xlsx где в первой колонке время, а во втрой тема\n"
                        " некоторе расписение для примера есть по умолчанию\n"
                        " /list - посмотреть текущее расписание\n"
                        " /fact - узнать случайную мысль (их не много)\n")
    global reminder_thread
    reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,))
    reminder_thread.start()

@bot.message_handler(commands=['fact'])
def action_request(message):
    list = [ "Используй Duolingo - простой способ не забыть язык и тренировать память",
             "Реже смотри телевизр - лучше подпишись на ленту новостей по своему выбору",
             "Пиши на Python рассказывая идею программы chatGPT - в мире уже все написано",
             "Не очень доверяй Линуксу и программам от githab - их писали такие же как ты"]
    random_fact = random.choice(list)
    bot.reply_to(message,f"Лови мысль: {random_fact}")

@bot.message_handler(commands=['shedule'])
def build_shedule(message):
    bot.reply_to(message,"построчно вводите время в формате НН:MM и тему напоминания через пробел,"
                     "обновленное расписание запустится тут же")
    chat_id = message.chat.id
    mxtopic = len(topic)
    for i in range(mxtopic):
        dummy = shedule.pop(0)
    topic.clear()

@bot.message_handler(commands=['list'])
def list_shedule(message):
    chat_id = message.chat.id
    for i in range(len(topic)):
        bot.send_message(chat_id, f"{shedule[i]}\t {topic[i]}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Проверяем, что это файл Excel
        if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or message.document.file_name.endswith('.xlsx'):
            mxtopic = len(topic)
            for i in range(mxtopic):
                dummy = shedule.pop(0)
            topic.clear()
            wb = load_workbook(BytesIO(downloaded_file))
            ws = wb.active  # Активный лист
            for row in ws.iter_rows(values_only=True):
                s_time = str(row[0])[:5]
                if check_time_fmt(s_time):
                    shedule.insert(len(topic), s_time)
                    topic.append(row[1])
        else:
            bot.reply_to(message, "Пожалуйста, отправьте файл в формате .xlsx.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    line = text.split()
    # надо прверять формат line[0]
    shdl_time = str(line[0])
    if  check_time_fmt(shdl_time):
        shedule.insert(len(topic), shdl_time)
        topic.append(text[len(shdl_time):])
    else:
        bot.send_message(chat_id,"что то не так c форматом времени, надо HH:MM\nпопробуйте снова")
def send_reminders(chat_id):
    while True:
        now = datetime.datetime.now().strftime('%H:%M')
        for k in range(len(topic)):
            if now == shedule[k]:
                markup = telebot.types.InlineKeyboardMarkup()
                like_button = telebot.types.InlineKeyboardButton("👍", callback_data=f"like_{k}")
                markup.add(like_button)
                bot.send_message(chat_id, topic[k])
                time.sleep(61)
        time.sleep(3)
@bot.callback_query_handler(func=lambda call: call.data.startswith("like_"))
def callback_like(call):
    try:
        # Обработка лайка
        bot.answer_callback_query(call.id, "Спасибо за лайк!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {str(e)}")

bot.polling(non_stop=True)