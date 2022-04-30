import ast
from email import message
from threading import currentThread 
import requests, json 
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

def delete_last_message_wait(message=None, call=None, remove_keyboard=False):
    try:
        get_user_data(message=message, call=call)
        chat_id = user_data['chat_id']
        last_message_id = int(user_data['last_message'])
        bot.delete_message(chat_id=chat_id, message_id=last_message_id)
        if remove_keyboard:
            last_message = bot.send_message(chat_id=chat_id, text='⏳', \
                reply_markup=types.ReplyKeyboardRemove())
        else:
            last_message = bot.send_message(chat_id=chat_id, text='⏳')
        user_data['last_message'] = last_message.id
        save_user_data(user_data, status)
    except:
        pass

def delete_last_message(message=None, call=None):
    try:
        get_user_data(message=message, call=call)
        chat_id = user_data['chat_id']
        last_message_id = int(user_data['last_message'])
        bot.delete_message(chat_id=chat_id, message_id=last_message_id)   
    except:
        pass
 

def inline_keyboard_maker(btns):
    markup = types.InlineKeyboardMarkup()
    for data, value in btns.items():
        markup.add(types.InlineKeyboardButton(text=value, callback_data=data))
    return markup 

def to_do_inline_keyboard_maker(tasks):
    buttons = []
    if tasks:
        for key, value in tasks.items():
            buttons.append([types.InlineKeyboardButton(text=value, callback_data="task {}".format(key))])
            edit_btns = []
            edit_btns.append(types.InlineKeyboardButton(callback_data="done {}".format(key), text="✅ done"))
            edit_btns.append(types.InlineKeyboardButton(callback_data="delete {}".format(key), text="🗑 remove"))
            buttons.append(edit_btns)
    #add_button
    buttons.append([types.InlineKeyboardButton(text=list(texts[user_lang]['to-do_add'].values())[0], \
        callback_data=list(texts[user_lang]['to-do_add'].keys())[0])])
    buttons.append([types.InlineKeyboardButton(text=list(texts[user_lang]['go_back_btn'].values())[0], \
        callback_data=list(texts[user_lang]['go_back_btn'].keys())[0])])
    markup = types.InlineKeyboardMarkup(buttons)
    return markup


def keyboard_button_maker(btns, request_location=False):
    markup = types.ReplyKeyboardMarkup()
    for btn in btns:
        markup.add(types.KeyboardButton(text=btn, request_location=request_location))
    return markup


#extra functions
def check_username(text):
    if len(text.split(' ')) == 1:
        return True
    else:
        return False 

def check_city(text):
    content_list = json.loads(requests.get(city_loc_checker_url.format(text, OW_API_KEY)).content)
    if len(content_list) != 0:
        content = content_list[0]
        message_text = texts[user_lang]['city_confirmation_text'].format(content["name"], content["country"])
        return message_text, content
    else:
        return "unknown", None

@bot.message_handler(commands=['start'])
def start_handler(message):
    global user_data, status, user_lang 
    get_user_data(message=message)
    if not get_user_data(message=message):
        user_data = {}
        status = 'lang_options'
        user_lang = None
        user_data["user_id"] = message.from_user.id
        user_data["chat_id"] = message.chat.id
        user_data["lang"] = user_lang
        user_data["status"] = status
        user_data["last_message"] = None
        user_data['all_tasks'] = "{}"
        user_data['current_tasks'] = "{}"
        user_data['done_tasks'] = "{}"
        user_data['deleted_tasks'] = "{}"
        save_user_data(user_data, status)
    else:
        status = "menu"
        save_user_data(user_data, status)
    return message_handler(message)


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
            reply_markup=keyboard_button_maker(texts[user_lang]['confirm_btns']), 
            parse_mode="MarkdownV2")
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
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['location_text'], 
            reply_markup=keyboard_button_maker(texts[user_lang]['location_btns'], request_location=True))
        user_data['last_message'] = last_message.message_id
        status = 'location'
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

def location_handler(message=None):
    get_user_data(message=message)
    delete_last_message_wait(message=message, remove_keyboard=True)
    delete_last_message(message=message)
    last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['menu_text'], 
        reply_markup=inline_keyboard_maker(texts[user_lang]['menu_btns']))
    user_data['last_message'] = last_message.message_id
    user_data["location"] = [message.location.latitude, message.location.longitude]
    status = "menu"
    save_user_data(user_data, status)


def location_text_handler(message=None):
    get_user_data(message=message)
    delete_last_message_wait(message=message, remove_keyboard=True)
    text = message.text
    if len(text.split(' ')) == 1:
        message_text, content = check_city(text)
        if message_text != "unknown":
            delete_last_message(message=message)
            last_message = bot.send_message(chat_id=user_data['chat_id'], \
                text=texts[user_lang]['city_confirmation_text'].format(content["name"], content["country"]), 
                reply_markup=keyboard_button_maker(texts[user_lang]['confirm_btns']),
                parse_mode="MarkdownV2")
            user_data['last_message'] = last_message.message_id
            user_data['location'] = [content['lat'], content["lon"]]
            status = "location_confirm"
            save_user_data(user_data, status)
        else:
            delete_last_message(message=message)
            last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['unknown_location_text'], 
                reply_markup=keyboard_button_maker(texts[user_lang]['location_btns'], request_location=True))
            user_data['last_message'] = last_message.message_id
            status = "location"
            save_user_data(user_data, status)
    else:
        delete_last_message(message=message)
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['wrong_location_type_text'], 
            reply_markup=keyboard_button_maker(texts[user_lang]['location_btns'], request_location=True))
        user_data['last_message'] = last_message.message_id
        status = "location"
        save_user_data(user_data, status)


def location_confirm_handler(message=None):
    get_user_data(message=message)
    delete_last_message_wait(message=message, remove_keyboard=True)
    delete_last_message(message=message)
    if message.text == "Yes":
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['menu_text'], 
            reply_markup=inline_keyboard_maker(texts[user_lang]['menu_btns']))
        user_data['last_message'] = last_message.message_id
        status = "menu"
        save_user_data(user_data, status)
    else:
        last_message = bot.send_message(chat_id=message.chat.id, text=texts[user_lang]['location_text'], 
            reply_markup=keyboard_button_maker(texts[user_lang]['location_btns'], request_location=True))
        user_data['last_message'] = last_message.message_id
        status = 'location'
        save_user_data(user_data, status)

def menu_maker(message=None, call=None):
    delete_last_message_wait(message=message, call=call)
    delete_last_message(message=message, call=call)
    chat_id = user_data['chat_id']
    last_message = bot.send_message(chat_id=chat_id, text=texts[user_lang]['menu_text'], 
        reply_markup=inline_keyboard_maker(texts[user_lang]['menu_btns']))
    user_data['last_message'] = last_message.message_id
    status = "menu"
    save_user_data(user_data, status)


#TO-DO-LIST
@bot.callback_query_handler(func=lambda call: call.data=="to-do-list")
def todolist_handler(call=None, message=None):
    get_user_data(message=message, call=call)
    delete_last_message_wait(message=message, call=call)
    tasks = ast.literal_eval(user_data['current_tasks'])
    if len(tasks) == 0:
        message_text = texts[user_lang]["to-do-list_empty_text"]
    else:
        message_text = texts[user_lang]["to-do-list_text"]
    delete_last_message(message=message, call=call)
    last_message = bot.send_message(chat_id=user_data['chat_id'], text=message_text, 
        reply_markup=to_do_inline_keyboard_maker(tasks=tasks))
    user_data['last_message'] = last_message.message_id
    status = "to-do-list"
    save_user_data(user_data, status)

@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_call_handler(call):
    get_user_data(call=call)
    delete_last_message_wait(call=call)
    delete_last_message(call=call)
    last_message = bot.send_message(chat_id=call.message.chat.id, text=texts[user_lang]['task_name'],
        reply_markup=inline_keyboard_maker(texts[user_lang]['go_back_btn']))
    user_data['last_message'] = last_message.message_id
    status = "add_task"
    save_user_data(user_data, status)

def add_task_handler(message):
    delete_last_message_wait(message=message)
    delete_last_message(message=message)
    task_name = message.text
    all_tasks = ast.literal_eval(user_data["all_tasks"])
    current_tasks = ast.literal_eval(user_data["current_tasks"])
    task_id = len(all_tasks) + 1
    all_tasks[task_id] = task_name
    current_tasks[task_id] = task_name
    user_data["all_tasks"] = str(all_tasks)
    user_data["current_tasks"] = str(current_tasks)
    status = 'to-do-list'
    save_user_data(user_data, status)
    return todolist_handler(message=message)
    
@bot.callback_query_handler(func=lambda call:call.data.startswith("done "))
def done_task_handler(call):
    get_user_data(call=call)
    task_id = int(call.data.split(" ")[1])
    current_tasks = ast.literal_eval(user_data["current_tasks"])
    done_tasks = ast.literal_eval(user_data['done_tasks'])
    done_tasks[task_id] = current_tasks[task_id]
    del current_tasks[task_id]
    user_data['current_tasks'] = str(current_tasks)
    user_data['done_tasks'] = str(done_tasks)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, 
        reply_markup=to_do_inline_keyboard_maker(tasks=current_tasks))
    save_user_data(user_data, status)

@bot.callback_query_handler(func=lambda call:call.data.startswith("delete "))
def done_task_handler(call):
    get_user_data(call=call)
    task_id = int(call.data.split(" ")[1])
    current_tasks = ast.literal_eval(user_data["current_tasks"])
    deleted_tasks = ast.literal_eval(user_data['done_tasks'])
    deleted_tasks[task_id] = current_tasks[task_id]
    del current_tasks[task_id]
    user_data['current_tasks'] = str(current_tasks)
    user_data['done_tasks'] = str(deleted_tasks)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, 
        reply_markup=to_do_inline_keyboard_maker(tasks=current_tasks))
    save_user_data(user_data, status)


@bot.callback_query_handler(func=lambda call: call.data=="birthdays")
def birthdays_handler(call=None, message=None):
    None

@bot.callback_query_handler(func=lambda call: call.data=="weather")
def weather_handler(call=None, message=None):
    None

@bot.callback_query_handler(func=lambda call: call.data=="settings")
def settings_handler(call=None, message=None):
    None





#location getter
@bot.message_handler(content_types=['location'])
def get_location(message):
    get_user_data(message=message)
    if status == 'location':
        return location_handler(message=message)


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
        elif status == "location":
            return location_text_handler(message=message)
        elif status == "location_confirm":
            return location_confirm_handler(message=message)
        elif status == "add_task":
            return add_task_handler(message)

#going back
@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back(call):
    get_user_data(call=call)
    if status in ["to-do-list"]:
        return menu_maker(call=call)
    elif status == "add_tisk":
        return todolist_handler(call=call)

bot.infinity_polling()