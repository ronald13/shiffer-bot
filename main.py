import telebot
from telebot import types
import os
import requests
import json
from config import config

bot = telebot.TeleBot(config.TELEBOT_TOKEN)


def save_token_to_file(token, file_name="token.txt"):
    with open(file_name, 'w') as file:
        file.write(token)

def load_token_from_file(file_name="token.txt"):
    try:
        with open(file_name, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Token file '{file_name}' not found.")
        return None
def get_token():
    credentials = {
        'email': config.API_SHIFFER_LOGIN,
        'password': config.API_SHIFFER_PASSWORD
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(config.API_SHIFFER_URL, json=credentials, headers=headers)
    if response.status_code == 200:
        try:
            token = response.json().get('token')
            save_token_to_file(token)
            print("Token saved to file")
        except json.JSONDecodeError:
            print("Error: Received non-JSON response")
    else:
        print("Failed to get token. Status Code:", response.status_code)



def generate_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Показать статистику', 'Авторизоваться')
    return markup

def generate_authorizated_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Личная статистику', 'Турнирную статистику', 'Меню')
    return markup

def generate_second_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Да', 'Нет', 'Назад')
    return markup

valid_emails = ["user1@example.com", "user2@example.com", "user3@example.com"]


def get_players_email_list():
    return valid_emails

def process_email_step(message):
    email = message.text
    if email in get_players_email_list():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Выслать еще раз', 'Назад')
        bot.send_message(message.chat.id, f"Вам выслан код на почту для подтверждения", reply_markup=markup)
        bot.register_next_step_handler(message, process_code_step)
    else:
        bot.reply_to(message, "Пользователь с таким email не найден. Попробуйте еще раз")
        bot.send_message(message.chat.id, "Введите ваш email:")
        bot.register_next_step_handler(message, process_email_step)

def process_code_step(message):
    code = message.text
    if code == "1234":
        markup = generate_authorizated_menu()
        bot.send_message(message.chat.id, "Вы успешно авторизовались", reply_markup=markup)
    else:
        bot.reply_to(message, "Код не верный. Попробуйте еще раз")
        bot.send_message(message.chat.id, "Введите код:")
        bot.register_next_step_handler(message, process_code_step)


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
    markup = generate_menu()
    bot.send_message(message.chat.id, "Привет! Я Шиффер Бот. Чем я могу тебе помочь?", reply_markup=markup)



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


bot.infinity_polling()