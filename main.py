import json
import telebot as tb
from telebot import types as tb_types

# Telegram Bot info
##########################
token = '7089389928:AAFhEBkRaV5zNqv7J5QDGbe2eEvRpznBnaU'
bot = tb.TeleBot(token)

id_list_user: dict = None
database_users: dict = None


##########################
# System function on bot.
##########################
@bot.message_handler(commands=['- Deleted'])
def deleted(message: tb_types.Message):
    pass


# __________ADD__________/
# Add - adding in system(user, ...).
@bot.message_handler(commands=['+ Add'])
def add(message: tb_types.Message):
    global database_users
    while True:
        object_list = ['#user', '#admin', '#list']
        bot.send_message(message.chat.id,
                         text=('#codes of object:\n'
                               '#user - add user in system\n'
                               'admin - add admin in system\n#list - to add list in database\n'
                               '#exit - to exit this function.'))

        command = bot.send_message(message.chat.id, text='Enter #name of object to adding in to the system:')

        if command not in object_list:
            bot.send_message(message.chat.id, text='Your # not in system parameter.')

        user_system_name = bot.send_message(message.chat.id, text='Enter the system name of user in database: ')
        user_id: str = bot.send_message(message.chat.id,
                                        text='Enter id of user, if you now this, if not write None')

        user_id_auth = False
        while not user_id_auth:

            if user_id == 'None':
                user_id_auth = True
                continue

            elif user_id.isalpha():
                bot.send_message(message.chat.id, text='ID cannot contain letters, please try again.')

            elif user_id.isdigit():
                user_id_auth = True
                continue

        first_name = bot.send_message(message.chat.id, text='Enter the first name of user: ')

        last_name = bot.send_message(message.chat.id, text='Enter the last name of user: ')

        database_users['admin' if command == '#admin' else 'user'][user_system_name] = {'user_id': user_id,
                                                                                        'first_name': first_name,
                                                                                        'lase_name': last_name}

        if command == '#list':
            list_name = bot.send_message(message.chat.id, text='Enter name of list: ')

            database_users.update({list_name: {}})


# ________UPGRADE________/
# Upgrade - change and save info of level user in database.
def upgrade(message: tb_types.Message):
    global id_list_user
    change = False
    # Retrieving data from id_list_of_user.json.
    try:
        with open('id_list_of_user.json', 'r', encoding='UTF-8') as read_file:
            id_list_user: dict = json.load(read_file)
    except FileNotFoundError:
        with open('id_list_of_user.json', 'w', encoding='UTF-8') as create_file:
            json.dump({}, create_file)

    if message.from_user.id not in id_list_user.keys():
        change = True
        id_list_user.update({message.from_user.id: authentication(message)})

    if change:
        with open('id_list_of_user.json', 'a', encoding='UTF-8') as update_file:
            json.dump(id_list_user, update_file)


# ____AUTHENTICATION____/
# Authentication - create level access.
def authentication(message: tb_types.Message):
    global database_users
    # Retrieving data from database_users.json.
    try:
        with open('database_users.json', 'r', encoding='UTF-8') as read_file:
            database_users: dict = json.load(read_file)
    except FileNotFoundError:
        with open('database_users.json', 'w', encoding='UTF-8') as create_file:
            json.dump({'programmer': {}, 'admin': {}, 'user': {}}, create_file)

    # Login for users in system.
    for list_class, users_list, in database_users.items():
        for user in users_list:
            # 1. User in system, user_id is in.
            if message.from_user.id in user['user_id']:
                match list_class:
                    case 'programmer':
                        return 'Full'
                    case 'admin':
                        return 'Admin'
                    case 'user':
                        return 'User'
            # 2. User in system, username is in, OR 3. User in system, user_first_name and(or) user_second_name is in.
            # Enter with password, for admin, ONLY.
            elif message.from_user.username in user['username'] or (message.from_user.first_name == user['first_name']
                                                                    and message.from_user.last_name == user[
                                                                        'second_name']):
                password_authentication = False
                while password_authentication is not True:

                    password = bot.send_message(message.chat.id, 'Write your enter password: ')
                    if list_class is 'admin':
                        try:
                            if password in user['password']:
                                password_authentication = True
                                return 'Admin'
                            else:
                                bot.send_message(message.chat.id, 'Your password, is not correct, please try again!')
                        except KeyError:
                            bot.send_message(message.chat.id,
                                             "You haven't got a password authentication, please contact to admin,"
                                             " or lead admin.")
                    elif list_class is 'user':
                        return 'User'

    # User not in system.
    return 'Quest'


# ________PANEL________/
# Panel - generate a work space for user.
def panel(level_user: str, message: tb_types.Message):
    markup = tb_types.ReplyKeyboardMarkup(resize_keyboard=True)

    if level_user is 'Full':
        add_button = tb_types.KeyboardButton(text='+ Add')
        deleted_button = tb_types.KeyboardButton(text='- Deleted')
        change_button = tb_types.KeyboardButton(text='/ Change')
        public_button = tb_types.KeyboardButton(text='# Public')
        zoolux_button = tb_types.KeyboardButton(text='|| Zoolux Database')

        markup.add(add_button, deleted_button)
        markup.add(change_button, zoolux_button)
        markup.add(public_button)

        bot.send_message(message.chat.id, text='', parse_mode='HTML', reply_markup=markup)

    elif level_user is 'Admin':

        public_button = tb_types.KeyboardButton(text='# Public')

        markup.add(public_button)
    elif level_user is 'User':

        unsubscribe_button = tb_types.KeyboardButton(text='@ Unsubscribe')

        markup.add(unsubscribe_button)
    elif level_user is 'Quest':

        subscribe_button = tb_types.KeyboardButton(text='* Subscribe')

        markup.add(subscribe_button)


# _________CORE_________/
# Core of Bot system
@bot.message_handler(commands=['start'])
def core(message: tb_types.Message):
    upgrade(message)

    panel(id_list_user[message.from_user.id], message)


bot.polling(none_stop=True)
