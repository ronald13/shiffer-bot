from datetime import datetime
import telebot
from telebot import types
import re
import requests
import json
from config import config
import pandas as pd
import random
import string
from send_mail import send_email
from markups import generate_menu, generate_authorizated_menu, generate_second_menu
from tokens import get_token, load_token_from_file


bot = telebot.TeleBot(config.TELEBOT_TOKEN)
tournament_list = ["КЧБ 2021", "КЧБ 2022", "КЧБ 2023"]

######################
#  Helper Functions  #
######################
def generate_random_code(length):
    characters = string.digits  # Using only digits (0-9)
    random_code = ''.join(random.choice(characters) for _ in range(length))
    return random_code

def process_email_after_nick_step(message, user_id=None):
    email = message.text
    if is_valid_email(email):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Выслать еще раз', 'Назад')
        bot.send_message(message.chat.id, f"Вам выслан код на почту для подтверждения", reply_markup=markup)
        code = generate_random_code(4)
        send_email(f"Код подтверждения", code, config.SENDER_EMAIL, email, config.SMTP_SERVER, config.SMTP_PORT, config.SMTP_USERNAME, config.SMTP_PASSWORD)
        bot.register_next_step_handler(message, process_code_step, code=code, user_id=user_id)
    else:
        bot.reply_to(message, "Email не валидный. Попробуйте еще раз")
        bot.send_message(message.chat.id, "Введите ваш email:")
        bot.register_next_step_handler(message, process_email_after_nick_step, user_id=user_id)



def send_code_to_email(email):
    code = generate_random_code(4)
    send_email("Код подтверждения", code, config.SENDER_EMAIL, email, config.SMTP_SERVER, config.SMTP_PORT, config.SMTP_USERNAME, config.SMTP_PASSWORD)
    return code

def player_validation_step():
    return "Chat_id записать в базу данных"

def process_nick_step(message):
    df = get_data_from_api()
    df = df[['id', 'name', 'email', 'player.name', 'club.name']]
    player_row = df.loc[df['player.name'] == message.text]
    players_list = player_row['player.name'].tolist()
    if len(players_list) == 0:
        bot.send_message(message.chat.id, "Такого пользователя не существует. Пройдите регистрацию на сайте shiffer.by", reply_markup=generate_menu())

    elif len(players_list) == 1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Отмена')
        bot.send_message(message.chat.id, f"Вы идентифицированы как {message.text}. Просьба ввести ваш email:", reply_markup=markup)
        bot.register_next_step_handler(message, process_email_after_nick_step, user_id=player_row['id'].tolist()[0])
        # # mail cохранить в базу данных. чтобы добавить на сайте
        # code_for_email = generate_random_code(4)
        # send_email(f"Код подтверждения", code_for_email, config.SENDER_EMAIL, player_row['email'].tolist()[0], config.SMTP_SERVER, config.SMTP_PORT, config.SMTP_USERNAME, config.SMTP_PASSWORD)
        # bot.register_next_step_handler(message, process_code_step, code=code_for_email, user_id=player_row['id'].tolist()[0], nick_name=message.text)

    elif len(players_list) > 1:
        bot.send_message(message.chat.id, "У вас несколько аккаунтов. Пожалуйста, укажите ваш клуб:")
        bot.register_next_step_handler(message, process_club_step)
def process_club_step(message):
    df = get_data_from_api()
    df = df[['id', 'name', 'email', 'player.name', 'club.name']]
    player_row = df.loc[df['player.name'] == message.text]
    club_list = player_row['club.name'].tolist()
    if message.text in club_list:
        bot.send_message(message.chat.id, "Сверяем ваши данные!")
        bot.register_next_step_handler(message, player_validation_step)
        # получаем id игрока
        # нужно записать код chat.id в базу данных. через api запрос
    else:
        bot.send_message(message.chat.id, "Такого клуба не существует. Пройдите регистрацию на сайте shiffer.by либо обратитесь в поддержку @shiffer_support", reply_markup=generate_menu())

def uthorizated_menu_answer(message):
    if message.text == "Личная статистика":

        keyboard = types.InlineKeyboardMarkup()
        for tournament in ["Клубные игры", "Турниры"]:
            button = types.InlineKeyboardButton(text=tournament, callback_data=f"tournament_{tournament}")
            keyboard.add(button)
        # Send message with inline buttons
        bot.send_message(message.chat.id, "Выбери:", reply_markup=keyboard)
    elif message.text == "Турнирную статистика":
        keyboard = types.InlineKeyboardMarkup()
        for tournament in tournament_list:
            button = types.InlineKeyboardButton(text=tournament, callback_data=f"tournament_{tournament}")
            keyboard.add(button)
        # Send message with inline buttons
        bot.send_message(message.chat.id, "Выбери турнир:", reply_markup=keyboard)
    elif message.text == "Меню":
        bot.reply_to(message, "Вы перешли в главное меню", reply_markup=generate_authorizated_menu())
        bot.register_next_step_handler(message, uthorizated_menu_answer)
    else:
        bot.reply_to(message, "Я не понимаю. Выберите команду из списка")
def is_valid_email(email):
    # Regular expression pattern for email validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Using re.match to check if the email matches the pattern
    if re.match(email_pattern, email):
        return True
    else:
        return False

def add_chat_id_to_db(message, user_id=None):
    token = load_token_from_file('token.txt')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'user_id': user_id,
        'telegram_chat_id': message.chat.id
    }
    response = requests.post(config.API_SHIFFER_ADD_CHAT_ID, headers=headers, json=data)
    if response.status_code == 200:
        print('chat_id записан в базу данных')
    return response.status_code

def get_data_from_api():

    token = load_token_from_file('token.txt')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(config.API_SHIFFER_URL_BOT,  headers=headers)
    if response.status_code == 200:
        try:
           data = response.json()
           return pd.json_normalize(data)
        except json.JSONDecodeError:
            print("Error: Received non-JSON response")
    else:
        print("Failed to get data. Status Code:", response.status_code)

def process_email_step(message, count_attempts=0, nick_name=None):
    email = message.text
    if is_valid_email(email):
        df = get_data_from_api()
        print('get_data_from_api', get_data_from_api())
        nick_name = df.loc[df['email'] == email, 'player.name'].tolist()
        print('nick_name', nick_name)
        if email in df['email'].tolist():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Выслать еще раз', 'Назад')
            bot.send_message(message.chat.id, f"Вам выслан код на почту для подтверждения", reply_markup=markup)
            code = generate_random_code(4)
            user_id = df.loc[df['email'] == email, 'id'].tolist()[0]
            send_email(f"Код подтверждения для {nick_name}", code, config.SENDER_EMAIL, email, config.SMTP_SERVER, config.SMTP_PORT, config.SMTP_USERNAME, config.SMTP_PASSWORD)
            print('nick_name=', nick_name, 'code=', code, 'user_id=', user_id)
            bot.register_next_step_handler(message, process_code_step, nick_name=nick_name, code=code, user_id=user_id)
        else:
            count_attempts += 1
            if count_attempts <= 2:
                bot.reply_to(message, "Пользователь с таким email не найден. Попробуйте еще раз")
                bot.send_message(message.chat.id, "Введите ваш email:")
                bot.register_next_step_handler(message, process_email_step, count_attempts=count_attempts)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add('Отмена')
                bot.send_message(message.chat.id, "Количество попыток превышено. Если вы уверены, что регистрировались на сайте, введите Ваш ник:", reply_markup=markup)
                bot.register_next_step_handler(message, process_nick_step)
    else:
        bot.reply_to(message, "Email не валидный. Попробуйте еще раз")
        bot.send_message(message.chat.id, "Введите ваш email:")
        bot.register_next_step_handler(message, process_email_step)

def process_code_step(message, nick_name=None, code=None, user_id=None):
    print('Вощед после введения ника', 'nick_name=', nick_name, 'code=', code,  'user_id=',user_id)
    code_from_message = message.text
    code_from_email = code

    if code_from_message == code_from_email:
        markup = generate_authorizated_menu()
        bot.send_message(message.chat.id, f"Вы успешно авторизовались {nick_name} with chat_id = {message.chat.id}", reply_markup=markup)
        # нужно записать код chat.id в базу данных. через api запрос
        bot.register_next_step_handler(message, add_chat_id_to_db, user_id=user_id)
    else:
        current_time = datetime.now()
        bot.reply_to(message, "Код не верный. Попробуйте еще раз")
        bot.send_message(message.chat.id, "Введите код:")
        bot.register_next_step_handler(message, process_code_step, code=code, nick_name=nick_name)


def is_registered_step(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Введите ваш email:")
        bot.register_next_step_handler(message, process_email_step)
    elif message.text == "Нет":
        markup = generate_menu()
        bot.send_message(message.chat.id, "Перейдите на сайт shiffer.by и зарегистрируйтесь", reply_markup=markup)
    elif message.text == "Назад":
        markup = generate_menu()
        bot.send_message(message.chat.id, "Вы перешли в главное меню", reply_markup=markup)
    else:
        bot.reply_to(message, "Я не понимаю. Выберите команду из списка")


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    df = get_data_from_api()

    if str(message.chat.id) in df['telegram_chat_id'].tolist():
        bot.send_message(message.chat.id, "Привет! Я Шиффер Бот. Чем я могу тебе помочь?", reply_markup=generate_authorizated_menu())
        bot.register_next_step_handler(message, uthorizated_menu_answer)
    else:
        print(df[df['name'] == 'Лютер'])
        bot.send_message(message.chat.id, "Привет! Я Шиффер Бот. Для дальнейшей работы нужно авторизоваться! ", reply_markup=generate_menu())


@bot.message_handler(commands=['help'])
def send_help_info(message):
    bot.reply_to(message, "Я могу помочь вам узнать статистику по вашим играм в Турнире. Просто выберите нужный пункт меню!")

get_token()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Показать статистику":
        bot.reply_to(message, "Какую статистику вы хотите увидеть?")
    elif message.text == "Авторизоваться":
        markup = generate_second_menu()
        bot.reply_to(message, "Вы регистрировались на сайте shiffer.by?", reply_markup=markup)
        bot.register_next_step_handler(message, is_registered_step)

    else:
        bot.reply_to(message, "Я не понимаю. Выберите команду из списка")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    for tournament in tournament_list:
        if call.data == f"tournament_{tournament}":
            bot.send_message(call.message.chat.id, f"You selected {tournament}")
            break
    for tournament in ["Клубные игры", "Турниры"]:
        if call.data == f"tournament_{tournament}":
            bot.send_message(call.message.chat.id, f"You selected {tournament}")
            break
bot.infinity_polling()