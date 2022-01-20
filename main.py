from imports import *  # Imports required for the bot to run
from functions import *  # Some important functions for teh bot to function
import time  # built in python library for logging purpose
import logging
# !!! Function to be called when the start command is called


def welcome(update: Update, context: CallbackContext):
    if update.message.chat.id in _ADMIN:  # !!! To check if the user is admin or not
        _USERS = LOGGINGCOLLECTION.find_one()['user']
        buttons = [[InlineKeyboardButton("Bot Activities", callback_data="activity")],
                   [InlineKeyboardButton("Send Anouncements", callback_data="anounce")]]
        context.bot.send_message(
            chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Welcome to ASTU Course Outline Robot\nChoose from the below choices to get started")

    else:
        # !!! If user is not admin
        _USERS = LOGGINGCOLLECTION.find_one()['user']
        userID = str(int(list(_USERS.keys())[-1])+1)
        query = {'userID': update.message.chat.id, 'firstName': update.message.chat.first_name,
                 'lastName': update.message.chat.last_name, 'userName': update.message.chat.username, 'logtime': dateConvert(list(time.localtime()))[0], 'currentTime': dateConvert(list(time.localtime()))[1]}
        _USERS[str(userID)] = query
        LOGGINGCOLLECTION.delete_one({'_id': 1})
        LOGGINGCOLLECTION.insert_one({'_id': 1, 'user': _USERS})
        buttons = [[InlineKeyboardButton("Get Started", callback_data="start")], [InlineKeyboardButton("Available Courses", callback_data="available")],
                   [InlineKeyboardButton("Search for course",
                                         callback_data="search")],
                   [InlineKeyboardButton("How to Use Me!", callback_data="usage")]]
        context.bot.send_message(
            chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Welcome to ASTU Course Outline Robot\nChoose from the below choices to get started")


# !!! Function to be called for browsing through the Course Outlines
def start(update: Update, context: CallbackContext, query: CallbackQuery):

    buttons = []
    _KEYS = list(_Courses.keys())
    for key in _KEYS:
        buttons.append([InlineKeyboardButton(key, callback_data=key)])
    buttons.append([InlineKeyboardButton(
        "<< Back", callback_data="back_start")])
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(
        buttons))
    context.user_data["current"] = []


# !!! Query handler that handles all iterations in the course outline database
def semHandler(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    current = context.user_data.get("current", [])
    # !! if the callback_data returnd value is start
    if text == "start":
        start(update, context, query)
    elif text == "usage":
        context.bot.send_video(chat_id=update.effective_chat.id,
                               video="BAACAgQAAxkBAAICWGHmmoYeuldkKLSJ2IQZ7cSkJDyBAAIwDgACcRQ4U7wNHAk5k86WIwQ")
    elif text == "available":
        button = [[InlineKeyboardButton("More ...", callback_data="more")]]
        ind = context.user_data["index"] = 0
        context.bot.send_message(
            chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(button), text='\n'.join(_OPTION[ind]), parse_mode='MarkDown')
        context.user_data["now"] = "search"
    elif text == "search":
        context.user_data["now"] = text
        query.edit_message_text(text="Send me the any course Title")
    else:
        # !!! used for the back functionality to go back to the previous stage
        if text == "back":
            current.pop()
        else:
            # !!! if the callback data is not back
            current.append(text)

        context.user_data["current"] = current
        tempD = _Courses
        for cur in current:
            tempD = tempD[cur]
        if type(tempD) == str:
            context.bot.send_document(
                chat_id=update.effective_chat.id, document=_CODE[tempD])
            current.pop()
        else:
            # !!! to send organized buttons to the user of the bot
            sendRequest(tempD, query, text, current)


# !!! inline Query hadler to handle inline querys from user outside the bot
def inlineQuery(update: Update, context: CallbackContext):
    query = update.inline_query.query

    if query == "":
        return
    _KEYS = list(_List.keys())
    tempKeys = []
    for key in _KEYS:
        if query.lower() in key.lower():
            tempKeys.append(key)
    result = []
    for i in tempKeys:
        result.append(InlineQueryResultCachedDocument(
            id=i+"_co",
            title=i,
            document_file_id=_List[i]
        ))

    update.inline_query.answer(result)


def messageHandler(update: Update, context: CallbackContext):
    if context.user_data.get("now", "") == "search":
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=_CODE[update.message.text])
    elif context.user_data.get("current", "") == "anounce":
        _user = USERSCOLLECTION.find_one()["users"]
        chats = []
        print(update.effective_chat.id)
        for id in _user:
            chats.append(int(id))
        print(chats)
        for chat in chats:
            context.bot.send_message(chat_id=chat, text=update.message.text)


def adminHandler(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data

    if text == 'activity':
        nowtime = dateConvert(list(time.localtime()))
        interval = nowtime[0] - 10
        tempDict = userGetter(interval)
        context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
            "Show all users", callback_data="users")]]), text=f'{len(tempDict)} activity(ies) in the last 10 minutes.')
        context.user_data["prev"] = tempDict
        context.user_data["current"] = text
    elif text == 'users':
        tempD = context.user_data.get("prev", {})
        if tempD:
            for user in tempD:
                context.bot.send_message(chat_id=update.effective_chat.id, text=str(
                    tempD[user]['firstName']) + " has started the bot at " + str(tempD[user]['currentTime']))
    elif text == 'anounce':
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="send my your anouncement")
        context.user_data["current"] = text


def moreHandler(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    ind = context.user_data.get("index", 0)
    if text == 'back_c':
        context.user_data["index"] -= 1
        if ind >= 0:
            button = [[InlineKeyboardButton(
                "More ...", callback_data="more")], [InlineKeyboardButton("<< Back", callback_data="back")]]
            query.edit_message_text(reply_markup=InlineKeyboardMarkup(
                button), text='\n'.join(_OPTION[ind]), parse_mode="MarkDown")
    elif text == 'more':
        tr
        context.user_data["index"] += 1
        if len(_OPTION) < ind+1:
            pass
        else:
            if _OPTION[ind]:
                button = [[InlineKeyboardButton(
                    "More ...", callback_data="more")], [InlineKeyboardButton("<< Back", callback_data="back_c")]]
            query.edit_message_text(reply_markup=InlineKeyboardMarkup(
                button), text='\n'.join(_OPTION[ind]), parse_mode="MarkDown")


def main():
    updater = Updater(key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", welcome))
    dispatcher.add_handler(CallbackQueryHandler(
        adminHandler, pattern=_adminpattern))
    dispatcher.add_handler(CallbackQueryHandler(
        moreHandler, pattern="more|back_c"))
    dispatcher.add_handler(CallbackQueryHandler(semHandler))
    dispatcher.add_handler(InlineQueryHandler(inlineQuery))
    dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    _adminstate = ['activity', 'users', 'anounce']
    _adminpattern = '('+')|('.join(_adminstate)+')'
    _ADMIN = [712156622]
    _Courses = OutlineCollection.find_one()['vals']
    _List = OutlineCollection.find_one()['courses']
    _CODE = OutlineCollection.find_one()['code']
    availableCourses = list(_CODE.keys())
    _OPTION = []
    total_index = len(availableCourses)//10
    reset = 0
    tempL = []
    for code in range(0, len(availableCourses)-1, 2):
        if reset == 5:
            reset = 0
            _OPTION.append(tempL)
            tempL = []
        else:
            tempL.append("`"+availableCourses[code] + "`" +
                         "        "+"`"+availableCourses[code+1] + "`")
            reset += 1

    main()
