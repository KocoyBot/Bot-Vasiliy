Бот Василий от Егора. Финальный проект для курса в котором я учусь.

Бот представляет собой общение с GPT и написание постов, с помощью GPT всё при помощи голоса.

Ссылка на бота: https://t.me/bekrenev_vasyliy_bot

Команды:

/start - регистрация в боте\n
/chat - общение с Василием\n
/post - написать пост\n
/help - помощь по командам\n
/buy - купить токены, символы, блоки\n
/values_valutes - ваши токены, символы, блоки\n
/debug - логи

Написан на Python, используя библиотеку PyTelegramBotAPI.

В проекте используются API: Telegram, Yandex GPT Pro и Yandex SpeechKit (Yandex Cloud).

bot.py - файл бота
config.py - константы бота
data_base.db - база данных бота
db.py - файл, где прописаны команды для обращении к базе данных
README.md - файл с описанием проекта
requirements.txt - список зависимостей
speechkit.py - файл, для работы с Yandex Speechkit
yandex_gpt.py - фалй, для работы с Yandex GPT
