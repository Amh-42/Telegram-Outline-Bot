from telegram.ext import *
from telegram import *
from Token import *
from mongodb import *
from mongodb import *

_USERS = LOGGINGCOLLECTION.find_one()['user']


def sendRequest(tempD, query, text, current):
    buttons = []
    keys = list(tempD.keys())
    key_len = len(keys)
    if key_len > 3:
        if key_len % 2 == 0:
            key1 = keys[:key_len//2]
            key2 = keys[key_len//2:]
            for key in range(key_len//2):
                buttons.append([InlineKeyboardButton(key1[key], callback_data=key1[key]),
                                InlineKeyboardButton(key2[key], callback_data=key2[key])])
        else:
            key1 = keys[:key_len//2]
            key2 = keys[key_len//2:key_len-1]
            for key in range(key_len//2):
                buttons.append([InlineKeyboardButton(key1[key], callback_data=key1[key]),
                                InlineKeyboardButton(key2[key], callback_data=key2[key])])
            buttons.append([InlineKeyboardButton(
                keys[-1], callback_data=keys[-1])])

    else:
        for key in keys:
            buttons.append(
                [InlineKeyboardButton(key, callback_data=key)])
    if current:
        buttons.append([InlineKeyboardButton(
            "<< Back", callback_data="back")])
    query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons))


def dateConvert(now):
    year = now[0] - 2022
    month = now[1] - 1
    day = now[2] - 1
    hour = now[3]
    minute = now[4]
    y_t_now = 525600 * year
    m_t_now = 43200 * month
    d_t_now = 1440 * day
    h_t_now = 60 * hour
    times = []
    times.append(y_t_now+m_t_now+d_t_now+h_t_now+minute)
    times.append(f'{hour}:{minute}')
    return times


def userGetter(log):
    _USERS = LOGGINGCOLLECTION.find_one()['user']
    d = {}
    tempD = _USERS
    for user in tempD:
        if tempD[user]['logtime'] >= log:
            d[user] = tempD[user]

    return d
