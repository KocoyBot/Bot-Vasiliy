import requests
import logging
import config

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def gpt(*args):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

    headers = {
        'Authorization': f'Api-Key {config.api_key}',
        'Content-Type': 'application/json'
    }

    json = {
            "modelUri": f"gpt://{config.folder_id}/yandexgpt/latest",
            "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": "500"
        },
            "messages": [i for i in args]
        }
    
    for i in args:
        json["messages"] = i

    try:
        resp = requests.post(url, headers=headers, json=json)

        if resp.status_code == 200:
            logging.info("YANDEX GPT: 200 OK")
            result = resp.json()["result"]["alternatives"][0]["message"]["text"]
            return result
        
        error_message = 'Invalid response received: code: {}, message: {}'.format(resp.status_code, resp.text)
        logging.error(f"YANDEX GPT: {error_message}")
        return error_message
    
    except Exception as e:
        logging.error(e)
        return e
    
def count_tokens(*args):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion'

    headers = {
        'Authorization': f'Api-Key {config.api_key}',
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{config.folder_id}/yandexgpt/latest",
       "messages": []
    }

    for i in args:
        data["messages"] = i

    try:
        resp = requests.post(url, json=data, headers=headers)

        if not(resp.json()['tokens']):
            logging.error(f"YANDEX GPT: произошла ошибка {resp.json()}")
            return resp.json()
        
        logging.info("YANDEX GPT: 200 OK")
        return len(resp.json()['tokens'])
    
    except Exception as e:
        logging.error(e)
        return e