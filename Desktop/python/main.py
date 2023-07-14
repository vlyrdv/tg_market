import telebot
from telebot import types
import sqlite3
from SimpleQIWI import *
import time
token = '5942354634:AAH_K3uxKnNNdWZD6VkmgQpvXm6-MTL-Q8Y'
bot = telebot.TeleBot(token)

qiwitoken = "d6e97d125007efb713a5791311c94c1e"
qiwiphone = "79218606022"
admin_users = [841653874, 603758804]
new_button_obj = {}
new_item_obj = {}
up_balance_obj = {}



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


class New_Item:
    def __init__(self, btn_id):
        self.btn_id = btn_id
        self.item_name = None
        self.item_key = None
        self.item_text = None


class UpBalance:
    def __init__(self, up_value):
        self.up_value = up_value
        self.start = None

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
        "INSERT INTO buttons (button_name, callback_data_btn) VALUES (?, ?)",
        [new_button_obj[msg.chat.id].btn_name, new_button_obj[msg.chat.id].btn_key])
    conn.commit()
    return cur.lastrowid


def select_buttons(conn): #доставание названий кнопок
    cur = conn.cursor()
    cur.execute("SELECT button_name, callback_data_btn FROM buttons")
    result = cur.fetchall()
    return result


def select_button_of_name(conn, btn_name): #доставание кнопки по имени
    cur = conn.cursor()
    cur.execute("SELECT * FROM buttons WHERE button_name=?", [btn_name])
    result = cur.fetchall()
    return result


def take_idbtn_of_name(conn, btn_name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM buttons WHERE button_name=?", [btn_name])
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
        res = insert_button(conn, msg)
        del new_button_obj[msg.chat.id]
        bot.send_message(msg.chat.id, "Кнопка успешно добавлена!")

# def itog_create_button(msg): #Добавление текста кнопки и добавление ее в базу
#     conn = db_connection()
#     res = insert_button(conn, msg)
#     del new_button_obj[msg.chat.id]
#     bot.send_message(msg.chat.id, "Кнопка успешно добавлена!")

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

def select_items_callbacks(conn):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT callback_data_item FROM items")
    result = cur.fetchall()
    return result


def select_items_of_callback_data(conn, req):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM buttons WHERE callback_data_btn=?", [req])
    result = cur.fetchall()
    print(result)

    cur2 = conn.cursor()
    cur2.execute("SELECT * FROM items WHERE button_id=?", [result[0][0]])
    res = cur2.fetchall()
    return res

def select_button_with_callback(conn, req):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM buttons WHERE callback_data_btn=?", [req])
    result = cur.fetchall()
    return result


def select_item_of_callback(conn, req):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE callback_data_item=?", [req])
    result = cur.fetchall()
    return result

def new_item_id(msg):
    conn = db_connection()
    res = take_idbtn_of_name(conn, msg.text)
    new_item_obj[msg.chat.id] = New_Item(res[0][0])
    mess = bot.send_message(msg.chat.id, "Введите имя товара")
    bot.register_next_step_handler(mess, new_item_name)

def new_item_name(msg):
    new_item_obj[msg.chat.id].item_name = msg.text
    mess = bot.send_message(msg.chat.id, "Введите ключ товара")
    conn = db_connection()
    mas = select_items_callbacks(conn)
    flag = False
    for i in mas:
        if i[0] == mess:
            flag = True
            break
    if flag:
        bot.send_message(msg.chat.id, "Такой ключ уже существует")
    else:
        bot.register_next_step_handler(mess, new_item_key)

def new_item_key(msg):
    new_item_obj[msg.chat.id].item_key = msg.text
    mess = bot.send_message(msg.chat.id, "Введите текст товара")
    bot.register_next_step_handler(mess, add_new_item)

def add_new_item(msg):
    new_item_obj[msg.chat.id].item_text = msg.text

    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (button_id, item_name, callback_data_item, item_text) VALUES (?, ?, ?, ?)",
        (new_item_obj[msg.chat.id].btn_id, new_item_obj[msg.chat.id].item_name,
         new_item_obj[msg.chat.id].item_key, new_item_obj[msg.chat.id].item_text))
    conn.commit()
    bot.send_message(msg.chat.id, "Товар успешно добавлен")

def delete_item(msg):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE callback_data_item = ?", [msg.text])
    result = cur.fetchall()
    if len(result) > 0:
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE callback_data_item = ?", [msg.text])
        conn.commit()
        bot.send_message(msg.chat.id, "Такой успешно удален!")
    else:
        bot.send_message(msg.chat.id, "Такой товар не найден!")

def up_balance(msg):
    bot.send_message(msg.chat.id, "Переведите")

    api = QApi(token=qiwitoken, phone=qiwiphone)
    up_balance_obj[msg.chat.id] = UpBalance(float(msg.text))
    up_balance_obj[msg.chat.id].start = api.balance

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Оплачено", callback_data="wellpay"))
    markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))

    bot.send_message(msg.chat.id, f"Переведите {msg.text} рублей на наш счет QIWQ: \n\n"
                                  f"79218606022\n"
                                  f"После перевода нажмите кнопку <b>оплачено</b>!\n\n"
                                  f"Если вы переведете не ту сумму или не на тот банк, то ваш платеж будет аннулирован",
                     reply_markup=markup, parse_mode="html")

def take_ref_pers(conn):
    cur = conn.cursor()
    cur.execute("SELECT percent FROM referal ")
    result = cur.fetchall()
    return result

def up_user_balance(conn, val):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET balance=? WHERE chat_id=?", val)
    conn.commit()

def check_referal_balance(conn, ref_code):
    cur = conn.cursor()
    cur.execute("SELECT balance FROM Users WHERE referal_code=? ", ref_code)
    result = cur.fetchall()
    return result

def up_referal_balance(conn, val):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Users SET balance=? WHERE referal_code=?", val)
    conn.commit()

def new_ref_proc(mess):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE referal SET persent=?", [mess.text])
    conn.commit()

    bot.send_message(mess.chat.id, "Вы успешно изменили реферальный процент")

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
        msg = bot.send_message(call.message.chat.id, "Введите сумму пополнеия")
        bot.register_next_step_handler(msg, up_balance)
    elif req == "wellpay":
        api = QApi(token=qiwitoken, phone=qiwiphone)
        bot.send_message(call.message.chat.id, "Проверяем платеж")
        time.sleep(3)
        print(up_balance_obj[call.message.chat.id].up_value)
        if api.balance[0] - up_balance_obj[call.message.chat.id].start[0] == up_balance_obj[call.message.chat.id].up_value:
            bot.send_message(call.message.chat.id, "Платеж не прошел, повторите снова")
        else:
            bot.send_message(call.message.chat.id, "Ваш платеж прошел успешно!")
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("SELECT friend_code FROM Users WHERE chat_id=? ", [call.message.chat.id])
            result = cur.fetchall()
            if result[0] != "-":
                # print(check_referal_balance(conn, result[0]))
                # print(take_ref_pers(conn)[0])
                # print(up_balance_obj[call.message.chat.id].up_value)
                ref_sum = float(check_referal_balance(conn, result[0])[0][0]) + up_balance_obj[call.message.chat.id].up_value * (float(take_ref_pers(conn)[0][0]) / 100)
                up_referal_balance(conn, [ref_sum, result[0][0]])
            up_user_balance(conn, [str(up_balance_obj[call.message.chat.id].up_value), call.message.chat.id])


            del up_balance_obj[call.message.chat.id]


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
    elif req == "new_item":
        msg = bot.send_message(call.message.chat.id, "Введите категорию товара")
        bot.register_next_step_handler(msg, new_item_id)
    elif req == "delete_item":
        msg = bot.send_message(call.message.chat.id, "Введите ключ товара")
        bot.register_next_step_handler(msg, delete_item)
    elif req == "new_ref_proc":
        mess = bot.send_message(call.message.chat.id, "Введите новый реферальный процент:")
        bot.register_next_step_handler(mess, new_ref_proc)
    else:
        conn = db_connection()
        mas = select_button_with_callback(conn, req)
        if len(mas) > 0:
            res = select_items_of_callback_data(conn, req)
            markup = types.InlineKeyboardMarkup()
            if len(res) == 0:
                markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
                bot.send_message(call.message.chat.id, "Товары в этой категории отсутствуют", reply_markup=markup)
            else:
                for i in res:
                    markup.add(types.InlineKeyboardButton(i[2], callback_data=i[3]))
                markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
                bot.send_message(call.message.chat.id, "Выберите товар", reply_markup=markup)
        else:
            conn = db_connection()
            res = select_item_of_callback(conn, req)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Назад", callback_data="go_back"))
            bot.send_message(call.message.chat.id, res[0][-1], reply_markup=markup)





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
        print(res)
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
            markup.add(types.InlineKeyboardButton("Добавить категорию", callback_data="new_button"), types.InlineKeyboardButton("Удалить категорию", callback_data="delete_button"))
            markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="new_item"),
                       types.InlineKeyboardButton("Удалить товар", callback_data="delete_item"))
            markup.add(types.InlineKeyboardButton("Изменить реф. процент", callback_data="new_ref_proc"))
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет прав на доступ к этой функции")
bot.polling(none_stop=True)



