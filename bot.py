import logging
import telebot
from telebot import types
import config
import db
import yandex_gpt
import speechkit
import json
import math

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = telebot.TeleBot(config.TOKEN)

def create_buttons(*args):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in args:
            markup.add(types.KeyboardButton(i))
        return markup
    except Exception as e:
        logging.error(e)
        return

@bot.message_handler(commands=['start'])
def start(message):
    try:
        if len(db.select_data(f"SELECT `user_id` FROM `users` WHERE `user_id` = '{message.from_user.id}'")) != 0:
            logging.info(f"{message.from_user.id}: Пользователь найден")
            bot.send_message(message.chat.id, 'KocoyBot: Здравствуйте, это бот Василий. С ним ты можешь общаться, а так же написать пост на любую тему. Пропиши /help, чтобы увидеть значения команд', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        db.set_query(f"INSERT INTO `users` (`user_id`, `tokens`, `symbols`, `blocks`) VALUES ('{message.from_user.id}', '{config.MAX_TOKENS_FOR_USER}', '{config.MAX_SYMBOLS_FOR_USERS}', '{config.MAX_BLOCKS_FOR_USERS}')")
        logging.info(f"{message.from_user.id}: Новый пользователь")
        bot.send_message(message.chat.id, 'KocoyBot: Здравcтвуйте, это бот Василий. С ним ты можешь общаться, а так же написать пост на любую тему. Пропиши /help, чтобы увидеть значения команд', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

@bot.message_handler(commands=['chat'])
def chat(message):
    try:
        if db.select_data(f"SELECT `symbols` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] == 0:
            bot.send_message(message.chat.id, 'KocoyBot: Недостаточно токенов, сиволов или блоков', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        if len(db.select_data(f"SELECT `user_id` FROM `messages` WHERE `user_id` = '{message.from_user.id}'")) == 0:
            bot.send_message(message.chat.id, 'KocoyBot: Запишите голосовое сообщение Василию', reply_markup=create_buttons('Новый чат', 'Удалить историю переписки и выйти', 'Выйти, сохранив историю переписки'))
            bot.register_next_step_handler(message, messaging)
        
        if len(db.select_data(f"SELECT `user_id` FROM `messages` WHERE `user_id` = '{message.from_user.id}'")) > 0:
            bot.send_message(message.chat.id, 'KocoyBot: Продолжите общаться с Василием, записав голосовое сообщение ему', reply_markup=create_buttons('Новый чат', 'Удалить историю переписки и выйти', 'Выйти, сохранив историю переписки'))
            bot.register_next_step_handler(message, messaging)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')
        return
    
def messaging(message):
    try:
        if db.select_data(f"SELECT `symbols` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] == 0:
            bot.send_message(message.chat.id, 'KocoyBot: Недостаточно токенов, сиволов или блоков', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        if message.text == 'Новый чат':
            db.set_query(f"DELETE FROM `messages` WHERE `user_id` = '{message.from_user.id}'")
            bot.send_message(message.chat.id, 'KocoyBot: Запишите голосовое сообщение Василию', reply_markup=create_buttons('Новый чат', 'Удалить историю переписки и выйти', 'Выйти, сохранив историю переписки'))
            bot.register_next_step_handler(message, messaging)
            return

        if message.text == 'Удалить историю переписки и выйти':
            db.set_query(f"DELETE FROM `messages` WHERE `user_id` = '{message.from_user.id}'")
            bot.send_message(message.chat.id, 'Вы закончили общаться', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        if message.text == 'Выйти, сохранив историю переписки':
            bot.send_message(message.chat.id, 'Вы закончили общаться, возращайтесь, чтобы продолжить', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        if message.content_type != 'voice':
            bot.send_message(message.chat.id, f'Запишите голосовое сообщение')
            bot.register_next_step_handler(message, messaging)
            return
        
        if message.voice.duration >= config.MAX_DURATION:
            bot.send_message(message.chat.id, f"Ваше аудио сообщение дольше 30 секунд, максимальная продолжительность аудио сообщения 30 секунд. Запишите аудио короче или же  секунд")
            bot.register_next_step_handler(message, messaging)
            return
        
        if speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[0] != True:
            bot.send_message(message.chat.id, speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[1])
            return
        
        db.set_query(f"UPDATE `users` SET `blocks` = '" + str(db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] - math.ceil(message.voice.duration / 15)) + f"' WHERE `user_id` = '{message.from_user.id}'")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'mess', 'system', '" + json.dumps({'role': 'system', 'text': f'{config.system_prompt[1]}'}, ensure_ascii=False) + "')")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'mess', 'user', '" + json.dumps({'role': 'user', 'text': f'{speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[1]}'}, ensure_ascii=False) + "')")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'mess', 'assistant', '" + json.dumps({'role': 'assistant', 'text': yandex_gpt.gpt(list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}'")))}, ensure_ascii=False) + "')")

        db.set_query(f"UPDATE `users` SET `tokens` = '" + str(db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] - yandex_gpt.count_tokens(list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}'")))) + f"' WHERE `user_id` = '{message.from_user.id}'")

        for i in list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}' AND `role` = 'assistant' ORDER BY `id` DESC LIMIT 1")):
            text = i['text']

        result = speechkit.text_to_speech(text)

        if result[0] == False:
            bot.send_message(message.chat.id, result[1])
            return
        
        bot.send_voice(message.chat.id, result[1])

        db.set_query(f"UPDATE `users` SET `symbols` = '" + str(db.select_data(f"SELECT `symbols` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] - len(text)) + f"' WHERE `user_id` = '{message.from_user.id}'")

        bot.register_next_step_handler(message, messaging)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

@bot.message_handler(commands=['post'])
def post(message):
    try:
        if db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] == 0:
            bot.send_message(message.chat.id, 'KocoyBot: Недостаточно токенов или блоков', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        bot.send_message(message.chat.id, "Запиши голосовое сообщение, где опишешь, о чём будет пост", reply_markup=create_buttons('Выйти из режима написания поста'))
        bot.register_next_step_handler(message, writing_post)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

def writing_post(message):
    try:
        if message.text == 'Выйти из режима написания поста':
            bot.send_message(message.chat.id, 'Вы вышли из режима написания постов', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return

        if db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] < 500 or db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] == 0:
            bot.send_message(message.chat.id, 'KocoyBot: Недостаточно токенов или блоков', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return
        
        if message.content_type != 'voice':
            bot.send_message(message.chat.id, 'Пожалуйста, запишите голосовое сообщение', reply_markup=create_buttons('Выйти из режима написания поста'))
            bot.register_next_step_handler(message, writing_post)
            return
        
        if message.voice.duration >= config.MAX_DURATION:
            bot.send_message(message.chat.id, f"Ваше аудио сообщение дольше 30 секунд, максимальная продолжительность аудио сообщения 30 секунд. Запишите аудио короче или же  секунд", reply_markup=create_buttons('Выйти из режима написания поста'))
            bot.register_next_step_handler(message, messaging)
            return
        
        if speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[0] != True:
            bot.send_message(message.chat.id, speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[1], reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
            return

        db.set_query(f"UPDATE `users` SET `blocks` = '" + str(db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] - math.ceil(message.voice.duration / 15)) + f"' WHERE `user_id` = '{message.from_user.id}'")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'post', 'system', '" + json.dumps({'role': 'system', 'text': f'{config.system_prompt[0]}'}, ensure_ascii=False) + "')")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'post', 'user', '" + json.dumps({'role': 'user', 'text': f'{speechkit.speech_to_text(bot.download_file(bot.get_file(message.voice.file_id).file_path))[1]}'}, ensure_ascii=False) + "')")

        db.set_query(f"INSERT INTO `messages` (`user_id`, `type`, `role`, `content`) VALUES ('{message.from_user.id}', 'post', 'assistant', '" + json.dumps({'role': 'assistant', 'text': yandex_gpt.gpt(list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}' AND `type` = 'post'")))}, ensure_ascii=False) + "')")

        db.set_query(f"UPDATE `users` SET `tokens` = '" + str(db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0] - yandex_gpt.count_tokens(list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}' AND `type` = 'post'")))) + f"' WHERE `user_id` = '{message.from_user.id}'")

        for i in list(json.loads(i) for i in db.select_data(f"SELECT `content` FROM `messages` WHERE `user_id` = '{message.from_user.id}' AND `role` = 'assistant' ORDER BY `id` DESC LIMIT 1")):
            text = i['text']

        db.set_query(f"DELETE FROM `message` WHERE `user_id` = '{message.from_user.id}' AND `type` = 'post'")

        db.set_query(f"INSERT INTO `posts` (`user_id`, `text`) VALUES ('{message.from_user.id}', '{text}')")

        bot.send_message(message.chat.id, 'Получившийся пост:\n' + db.select_data(f"SELECT `text` FROM `posts` WHERE `user_id` = '{message.from_user.id}' ORDER BY `id` DESC LIMIT 1")[0], reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')
    

@bot.message_handler(commands=['debug'])
def debug(message):
    try:
        with open(config.LOGS, 'r') as f:
            bot.send_document(message.chat.id, f, reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

@bot.message_handler(commands=['help'])
def help(message):
    try:
        bot.send_message(message.chat.id, '/chat - общение с Василием\n/post - написать пост\n/help - помощь по командам\n/buy - купить токены, символы, блоки\n/values_valutes - ваши токены, символы, блоки\n/debug - логи', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

@bot.message_handler(commands=['values_valutes'])
def values_valutes(message):
    try:
        bot.send_message(message.chat.id, 'Токенов: ' + str(db.select_data(f"SELECT `tokens` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0]) + '\nСимволов: ' + str(db.select_data(f"SELECT `symbols` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0]) + '\nБлоков: ' + str(db.select_data(f"SELECT `blocks` FROM `users` WHERE `user_id` = '{message.from_user.id}'")[0]))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

@bot.message_handler(commands=['buy'])
def buy(message):
    try:
        bot.send_message(message.chat.id, 'Для покупки, токенов, символов, блоков напишите сюда: https://t.me/xd_kocoy_bot_xd', reply_markup=create_buttons('/chat', '/post', '/help', '/buy', '/values_valutes', '/debug'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'Произошла ошибка {e}')

bot.infinity_polling()
