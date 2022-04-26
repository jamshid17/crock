
from site import USER_SITE
import telebot 
from  constants import *
import pandas as pd
from telebot import types





bot = telebot.TeleBot(API_KEY)
pd.set_option('mode.chained_assignment', None)
users_data = pd.read_csv("db/users_data.csv")


def get_user_data(message=None, call=None):
    global user_data, user_lang, status
    if message:
        user_id = message.from_user.id
    elif call:
        user_id = call.from_user.id 
    else:
        raise NameError
    if user_id not in users_data['user_id'].to_list():
        return False
    else:
        user_index = users_data.index[users_data['user_id'] == user_id][0]    
        user_data = users_data.to_dict('index')[user_index]
        status = user_data['status']
        user_lang = user_data['lang']
        return True

def save_user_data(current_user_data, current_status):
    global users_data
    current_user_data['status'] = current_status
    if users_data[users_data['user_id'] == current_user_data['user_id']].empty:
        current_user_data_df = pd.DataFrame(current_user_data, index=[0])  
        users_data = pd.concat([users_data, current_user_data_df]).reset_index(drop=True)
    else:
        current_user_index = users_data.index[users_data['user_id'] == current_user_data['user_id']][0]
        for key, value in current_user_data.items():
            users_data[key][current_user_index] = value
    users_data.to_csv('db/users_data.csv', index=False)

def delete_last_message_wait(message, remove_keyboard=False):
    get_user_data(message=message)
    last_message_id = int(user_data['last_message'])
    bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
    if remove_keyboard:
        last_message = bot.send_message(chat_id=message.chat.id, text='⏳', \
            reply_markup=types.ReplyKeyboardRemove())
    else:
        last_message = bot.send_message(chat_id=message.chat.id, text='⏳')
    user_data['last_message'] = last_message.id
    save_user_data(user_data, status)
    

def delete_last_message(message):
    get_user_data(message=message)
    last_message_id = int(user_data['last_message'])
    bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)   

 

def inline_keyboard_maker(btns):
    markup = types.InlineKeyboardMarkup()
    for data, value in btns.items():
        markup.add(types.InlineKeyboardButton(text=value, callback_data=data))
    return markup 

def keyboard_button_maker(btns):
    markup = types.ReplyKeyboardMarkup()
    for btn in btns:
        markup.add(types.KeyboardButton(text=btn))
    return markup

#extra functions
def check_username(text):
    if len(text.split(' ')) == 1:
        return True
    else:
        return False 


@bot.message_handler(commands=['start'])
def start_handler(message):
    global user_data, status, user_lang 
    get_user_data(message=message)
    if not get_user_data(message=message):
        print("PROBLEM")
        user_data = {}
        status = 'lang_options'
        user_lang = None
        user_data["user_id"] = message.from_user.id
        user_data["chat_id"] = message.chat.id
        user_data["lang"] = user_lang
        user_data["status"] = status
        user_data["last_message"] = None
        save_user_data(user_data, status)
    return message_handler(message)
    
def test_web_app(message):
    last_message = bot.send_message(chat_id=message.chat.id, text=texts['eng']['lang'], \
        reply_markup=inline_keyboard_maker(test_btns))    


def lang_presenter(message=None):
    get_user_data(message=message)
    last_message = bot.send_message(chat_id=message.chat.id, text=texts['eng']['lang'], \
        reply_markup=keyboard_button_maker(texts['eng']['lang_btns']))
    user_data['last_message'] = last_message.message_id
    status = 'get_lang'
    save_user_data(user_data, status)



def lang_handler(message):
    get_user_data(message=message)
    delete_last_message_wait(message=message, remove_keyboard=True)
    if message.text == "🇺🇿 O'zbek tili":
        user_lang = 'uz'
    elif message.text == "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English language":
        user_lang = 'eng'
    else:
        delete_last_message(message=message)
        return lang_handler(message=message)
    delete_last_message(message=message)
    last_message = bot.send_message(chat_id=message.chat.id, \
        text=texts[user_lang]["send_username"])
    user_data['last_message'] = last_message.message_id
    user_data['lang'] = user_lang
    status = 'get_username'
    save_user_data(user_data, status)

def username_handler(message):
    get_user_data(message=message)
    delete_last_message_wait(message=message)
    username = message.text
    if check_username(username):
        delete_last_message(message=message)
        last_message = bot.send_message(chat_id=message.chat.id, \
            text=texts[user_lang]['confirm_username'].format(username),
            reply_markup=keyboard_button_maker(texts[user_lang]['confirm_btns']))
        user_data['username'] = username 
        user_data['last_message'] = last_message.message_id
        status = 'confirm_username'
        save_user_data(user_data, status)
    else:
        delete_last_message(message=message)
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['wrong_type_username'])
        user_data['last_message'] = last_message.message_id

def confirm_username(message):
    get_user_data(message=message)
    delete_last_message_wait(message=message, remove_keyboard=True)
    delete_last_message(message=message)
    if message.text == "Yes":
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['menu_text'], 
            reply_markup=inline_keyboard_maker(texts[user_lang]['menu_btns']))
        user_data['last_message'] = last_message.message_id
        status = 'menu'
        save_user_data(user_data, status)
    elif message.text == "No, let me give you a new one":
        last_message = bot.send_message(chat_id=message.chat.id, \
            text=texts[user_lang]["send_username"])
        user_data['last_message'] = last_message.message_id
        status = "get_username"
        user_data['username'] = None
        save_user_data(user_data, status)
    else:
        last_message = bot.send_message(chat_id=message.chat.id, \
            text=texts[user_lang]['confirm_username'].format(user_data['username']),
            reply_markup=keyboard_button_maker(texts[user_lang]['confirm_btns']))
        user_data["last_message"] = last_message.message_id
        save_user_data(user_data, status)

def menu_maker(message):
    delete_last_message_wait(message=message)
    delete_last_message(message=message)
    last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['menu_text'], 
        reply_markup=inline_keyboard_maker(texts[user_lang]['menu_btns']))
    user_data['last_message'] = last_message.message_id
    save_user_data(user_data, status)


    
@bot.message_handler(func=lambda m: True)
def message_handler(message):
    get_user_data(message=message)
    print(status)
    if user_data["status"] == None:
        bot.send_message(chat_id=message.chat.id, text='chunmadim')
    else:
        if status == "lang_options":
            return lang_presenter(message=message)
        elif status == "get_lang":
            return lang_handler(message=message)
        elif status == "get_username":
            return username_handler(message=message)
        elif status == "confirm_username":
            return confirm_username(message=message)
        elif status == "menu":
            return menu_maker(message=message)
    



bot.infinity_polling()