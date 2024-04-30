import sqlite3
import config
import logging

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def select_data(sql):
    try:
        connection = sqlite3.connect(config.db_name)
        cursor = connection.cursor()
        list = []
        ex = cursor.execute(sql).fetchall()
        connection.close()
        for i in ex:
            for j in i:
                list.append(j)
        logging.info(f"DATABASE: вернулись данные {list}")
        return list
    
    except Exception as e:
        logging.error(e)
        return False, f'Произошла ошибка: {e}'

def set_query(sql):
    try:
        connection = sqlite3.connect(config.db_name)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        connection.close()
        logging.info(f"DATABASE: выполнен запрос {sql}")
    except Exception as e:
        logging.error(e)
        return False, f'Произошла ошибка: {e}'