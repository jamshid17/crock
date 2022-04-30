import pandas as pd 
import requests, json

from constants import OW_API_KEY 
import json
import telebot
from telebot import types
import re
tasks = {"task1":"going to gym", "task2":"lol"}
output = pd.DataFrame()
output = output.append(tasks, ignore_index=True)
print(output.head())


# print(LANGUAGE_DATA['uz']['orqaga_qaytish']['orqaga_qaytish'])
print("clear")


BOT_API = '5201537448:AAGlH5-TiZgdLaYvHgnZDijk2RRR8P1dE3w'

bot = telebot.TeleBot(BOT_API)
# tasks = {"task1":"going to gym", "task2":"lol"}
# switch_inline_querysdfsdfdfxfxdfxdzxfzxfzxfxfzzxdzxf
lst_items = {'restoranlar':'🍽 Restoranlar', 'kartalar':'💳 Kartalar'}
del lst_items["restoranlar"]
print(lst_items)
def makeInlineKeyboard(): 
    buttons = []
    
    for key, value in tasks.items():
        buttons.append([types.InlineKeyboardButton(text=value, callback_data=key)])
        edit_btns = []
        edit_btns.append(types.InlineKeyboardButton(callback_data="done", text="✅ done"))
        edit_btns.append(types.InlineKeyboardButton(callback_data="delete", text="🗑 remove"))
        buttons.append(edit_btns)

    # edit_btns = []
    # edit_btns.append(types.InlineKeyboardButton(callback_data="done", text="✅"))
    # edit_btns.append(types.InlineKeyboardButton(callback_data="delete", text="🗑"))
    # lst.append(edit_btns)
    markup = types.InlineKeyboardMarkup(buttons)
    print(buttons)
    return markup
    # markup.add(types.InlineKeyboardButton(text="Inline mode", switch_inline_query_current_chat=""))

def make_reply_keyboard():
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton(text="Xa tasdiqlayman"))
    markup.add(types.KeyboardButton(text="O'zgatiramiza"))
    return markup

# def make_remove_keyboard():
#     types.ReplyKeyboardRemove()
#     for 


@bot.message_handler(commands=['start'])
def start_handler(message): 
    print("sad")
    global bot_last_message 
    bot_last_message = bot.send_message(chat_id=message.chat.id, text="*\(Jamshid\)* \(Jabborov\)", 
        reply_markup=makeInlineKeyboard(),
        parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == 'kartalar')
def func(call):
    print(call.from_user.id)
    print(call.message.chat.id)

@bot.message_handler(func=lambda message: message.text == 'Xa tasdiqlayman')
def message_handler(message): 
    not_deleted = bot.send_message(message.chat.id, 
        text="⏳", reply_markup=types.ReplyKeyboardRemove())
    bot.delete_message(message.chat.id, message_id=not_deleted.message_id)
    bot.send_message(message.chat.id, text='Uchirild') 




@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'default', types.InputTextMessageContent('default'))
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


bot.infinity_polling()