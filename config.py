TOKEN = '' # Токен бота
folder_id = '' # ID каталога
api_key = '' # API ключ, вместо IAM токена, чтобы не писать функцию для сметы IAM токена
db_name = 'data_base.db' # Имя базы данных
LOGS = 'logs.txt' # Файл логов

MAX_TOKENS_FOR_USER = 15000
MAX_SYMBOLS_FOR_USERS = 10000
MAX_BLOCKS_FOR_USERS = 50
MAX_DURATION = 30

system_prompt = ["Ты - профессиональный сочинитель постов, составь пост без своих пометок, про то что попросил пользователь", 'Ты веселый собеседник. Тебя зовут Василий. Общайся с пользователем на "ты" и используй юмор. Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. Изображай человека. При этом не делай пометки по типу: "Василий: какой-то текст".']