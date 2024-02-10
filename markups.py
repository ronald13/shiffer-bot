from telebot import types


def generate_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Показать статистику', 'Авторизоваться')
    return markup

def generate_authorizated_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Личная статистика', 'Турнирную статистика', 'Меню')

    return markup

def generate_second_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Да', 'Нет', 'Назад')
    return markup

