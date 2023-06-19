import telebot
from telebot import types
import sqlite3
token = '5942354634:AAH_K3uxKnNNdWZD6VkmgQpvXm6-MTL-Q8Y'
bot = telebot.TeleBot(token)
admin_users = [841653874, 603758804]
new_button_obj = {}


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("./telegram_shop.db")
    except:
        print("ERROR")
    return conn


class New_Button:
    def __init__(self, btn_name):
        self.btn_name = btn_name
        self.btn_key = None
        self.btn_text = None

def select_chat_id(conn, chat_id): #проверка регистрации юзера
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users Where chat_id=?", (chat_id,))
    result = cur.fetchall()
    return result

def insert_user(conn, chat_id): #регистрация юзера
    ref_code = create_referal_code(chat_id)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Users (chat_id, balance, referal_code, friend_code) VALUES (?, ?, ?, ?)", (chat_id, "0", ref_code, "-"))
    conn.commit()

def select_users_id(conn): #доставание chat_id пользователей
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM Users")
    result = cur.fetchall()
    return result

def take_referal_code(conn, chat_id):
    cur = conn.cursor()
    cur.execute("SELECT referal_code FROM Users WHERE chat_id=?", [chat_id])
    result = cur.fetchall()
    return result

def distribution(msg): #рассылка
    print(msg.text)
    conn = db_connection()
    res = select_users_id(conn)
    for i in res:
        if msg.chat.id not in admin_users:
            try:
                bot.send_message(i[0], msg.text)
            except BaseException:
                pass
    bot.send_message(msg.chat.id, "Рассылка выполнена успешно!")


def insert_button(conn, msg):  # Добавление товара
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO buttons (button_name, callback_data_btn, button_text) VALUES (?, ?, ?)",
        [new_button_obj[msg.chat.id].btn_name, new_button_obj[msg.chat.id].btn_key, new_button_obj[msg.chat.id].btn_text])
    conn.commit()
    return cur.lastrowid


def select_buttons(conn): #доставание названий кнопок
    cur = conn.cursor()
    cur.execute("SELECT button_name, callback_data_btn FROM buttons")
    result = cur.fetchall()
    return result

def select_buttons_text(conn, req): #доставание текста на кнопки
    cur = conn.cursor()
    cur.execute("SELECT button_text FROM buttons WHERE callback_data_btn=?", [req])
    result = cur.fetchall()
    return result


def select_button_of_name(conn, btn_name): #доставание кнопки по имени
    cur = conn.cursor()
    cur.execute("SELECT * FROM buttons WHERE button_name=?", [btn_name])
    result = cur.fetchall()
    return result


def check_or_create_new_button(msg): #Проверка на существование кнопки, в противном случае создание новой
    conn = db_connection()
    res = select_buttons(conn)
    flag = False
    for i in res:
        if i[0] == msg.text:
            flag = True
            break
    if flag:
        bot.send_message(msg.chat.id, "Такая кнопка уже существует")
    else:
        new_button_obj[msg.chat.id] = New_Button(msg.text)
        mess = bot.send_message(msg.chat.id, "Введите ключ кнопки")
        bot.register_next_step_handler(mess, check_or_create_new_button2)


def check_or_create_new_button2(msg): #добавление ключа кнопки
    conn = db_connection()
    res = select_buttons(conn)
    flag = False
    for i in res:
        if i[-1] == msg.text:
            flag = True
            break
    if flag:
        bot.send_message(msg.chat.id, "Такой ключ уже существует")
    else:
        new_button_obj[msg.chat.id].btn_key = msg.text
        mess = bot.send_message(msg.chat.id, "Введите текст для кнопки")
        bot.register_next_step_handler(mess, itog_create_button)


def itog_create_button(msg): #Добавление текста кнопки и добавление ее в базу
    new_button_obj[msg.chat.id].btn_text = msg.text
    conn = db_connection()
    res = insert_button(conn, msg)
    del new_button_obj[msg.chat.id]
    bot.send_message(msg.chat.id, "Кнопка успешно добавлена!")

def delete_button(conn, btn_name): #удаление кнопки по имени
    cur = conn.cursor()
    cur.execute("DELETE FROM buttons WHERE button_name = ?", [btn_name])
    conn.commit()

def check_delete_button(msg):
    conn = db_connection()
    res = select_button_of_name(conn, msg.text)
    print(res)
    if len(res) == 0:
        bot.send_message(msg.chat.id, "Такая кнопка отсутсвует")
    else:
        print(msg.text)
        res = delete_button(conn, msg.text)
        bot.send_message(msg.chat.id, "Кнопка успешно удалена!")

def create_referal_code(chat_id): #создание рефералки
    mas = list(str(chat_id))
    itog_str = ""
    hash_ = "%mcdb591fhjsncfr"
    for i in range(len(mas)):
        itog_str += mas[i]
        itog_str += hash_[i]
    return itog_str


def take_my_referal(conn, chat_id): #доставание рефералки по chat_id
    cur = conn.cursor()
    cur.execute("SELECT referal_code FROM Users WHERE chat_id=?", [chat_id])
    result = cur.fetchall()
    return result

def use_referal_friend(conn, chat_id): #проверка на использование реферальной ссылки
    cur = conn.cursor()
    cur.execute("SELECT friend_code FROM Users WHERE chat_id=?", [chat_id])
    result = cur.fetchall()
    return result

def change_referal_code(msg):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET friend_code=? WHERE chat_id=?", [msg.text, msg.chat.id])
    conn.commit()

def verification_referal_code(msg): #проверка реферального кода
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE referal_code=?", [msg.text])
    result = cur.fetchall()
    if len(result) > 0:
        change_referal_code(msg)
        bot.send_message(msg.chat.id, "Вы успешно присоединились по реферальной ссылке")
        bot.send_message(result[0][1], f"{msg.from_user.username} присоединился к вам по реферальной ссылке")
    else:
        bot.send_message(msg.chat.id, "Реферальный код не найден")

@bot.callback_query_handler(func=lambda call:True) #ответы на работу кнопок
def callback_query(call):
    req = call.data
    if req == 'unseen':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif req == "go_back":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif req == "go_back2":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    elif req == "replenish_balance":
        pass
        #Пополнение баланса
    elif req == "new_button":
        msg = bot.send_message(call.message.chat.id, "Введите имя кнопки")
        bot.register_next_step_handler(msg, check_or_create_new_button)
    elif req == "delete_button":
        msg = bot.send_message(call.message.chat.id, "Введите имя кнопки")
        bot.register_next_step_handler(msg, check_delete_button)
    elif req == "referral_system":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Мой код", callback_data="my_code"),
                   types.InlineKeyboardButton("Ввести код друга", callback_data="friend_code"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
        bot.send_message(call.message.chat.id, "Выберите нужное действие", reply_markup=markup)
    elif req == "my_code":
        conn = db_connection()
        res = take_referal_code(conn, call.message.chat.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
        bot.send_message(call.message.chat.id, f"Ваш реферальный ко <b>{res[0][0]}</b>",
                         reply_markup=markup, parse_mode="html")
    elif req == "friend_code":
        conn = db_connection()
        res = use_referal_friend(conn, call.message.chat.id)
        if res[0][0] != "-":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
            bot.send_message(call.message.chat.id, "Вы уже вводили реферальный код", reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
            msg = bot.send_message(call.message.chat.id, "Введите код друга", reply_markup=markup)
            bot.register_next_step_handler(msg, verification_referal_code)
    else:
        conn = db_connection()
        res = select_buttons_text(conn, req)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
        bot.send_message(call.message.chat.id, res[0][0], reply_markup=markup)






@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Категории"), types.KeyboardButton("Профиль"))
    if message.chat.id in admin_users:
        markup.add(types.KeyboardButton("Рассылка"))
        markup.add(types.KeyboardButton("Админка"))
    bot.send_message(message.chat.id, "Привет", reply_markup=markup)




@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Категории":
        markup = types.InlineKeyboardMarkup()
        conn = db_connection()
        res = select_buttons(conn)
        for i in res:
            markup.add(types.InlineKeyboardButton(i[0], callback_data=i[-1]))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back2"))
        bot.send_message(message.chat.id, text="Выберите интересующую категорию", reply_markup=markup)
    elif message.text == "Профиль":
        conn = db_connection()
        res = select_chat_id(conn, message.chat.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Пополнить баланс", callback_data="replenish_balance"))
        markup.add(types.InlineKeyboardButton("Реферальная система", callback_data="referral_system"))

        if len(res) == 0:
            insert_user(conn, message.chat.id)
            bot.send_message(message.chat.id, f"❤️ Имя: <b>{message.from_user.first_name}</b> \n"
                                              f"💰 Ваш баланс: <b>0</b>", reply_markup=markup,
                             parse_mode="html")
        else:
            bot.send_message(message.chat.id, f"❤️ Имя: <b>{message.from_user.first_name}</b> \n"
                                              f"💰 Ваш баланс: <b>{float(res[-1][2])}</b>", reply_markup=markup, parse_mode="html")
    elif message.text == "Рассылка":
        if message.chat.id in admin_users:
            msg = bot.send_message(message.chat.id, "Введите текст рассылки")
            bot.register_next_step_handler(msg, distribution)

        else:
            bot.send_message(message.chat.id, "У вас нет прав на доступ к этой функции")
    elif message.text == "Админка":
        if message.chat.id in admin_users:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Добавить кнопку", callback_data="new_button"))
            markup.add(types.InlineKeyboardButton("Удалить кнопку", callback_data="delete_button"))
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет прав на доступ к этой функции")
bot.polling(none_stop=True)


