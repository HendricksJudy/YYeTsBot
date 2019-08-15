# coding: utf-8
# YYeTsBot - bot.py
# 2019/8/15 18:27

__author__ = 'Benny <benny.think@gmail.com>'

import os
import logging
import telebot
from telebot import apihelper
from config import TOKEN
from telebot import types
from utils import bunch_upsert, get

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

apihelper.proxy = {'socks5': 'socks5://127.0.0.1:1080'}

bot = telebot.TeleBot(os.environ.get('TOKEN') or TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, '欢迎使用，发送想要的剧集标题，我会帮你搜索')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, '''机器人无法使用或者报错？
    @BennyThink 或者<a href='https://github.com/BennyThink/YYeTsBot/issues'>Github issues</a>''',
                     parse_mode='html')


from html_parser import parser
from html_request import get_html


@bot.message_handler()
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'record_video')
    name = message.text
    logging.info('Receiving message about %s from user %s(%s)' % (name, message.chat.username,
                                                                  message.chat.id))
    # get html content
    contents = get_html(name)
    # get download link
    bot.send_chat_action(message.chat.id, 'upload_video')
    list_r, dict_r = [], {}
    for content in contents:
        r1, r2 = parser(content)
        list_r.extend(r1)
        dict_r = dict(dict_r, **r2)
    if not dict_r:
        bot.send_chat_action(message.chat.id, 'find_location')
        bot.send_message(message.chat.id, "没有找到您想要的信息🤪")
        return

    # saved dict_r
    bunch_upsert(dict_r)

    markup = types.InlineKeyboardMarkup()
    for item in list_r:
        btn = types.InlineKeyboardButton(item['name'], callback_data=item['id'])
        markup.add(btn)

    bot.send_chat_action(message.chat.id, 'upload_document')
    bot.send_message(message.chat.id, "点击按钮获取下载链接", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    bot.send_chat_action(call.message.chat.id, 'typing')
    dict_r = get(call.data)
    bot.answer_callback_query(call.id, '文件大小为%s' % dict_r['size'])
    bot.send_message(call.message.chat.id, dict_r['ed2k'])
    bot.send_message(call.message.chat.id, dict_r['magnet'])


if __name__ == '__main__':
    logging.info('YYeTs bot is running...')
    bot.polling()