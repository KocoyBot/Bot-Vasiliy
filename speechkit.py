import requests
import config
import logging

def text_to_speech(text: str):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

    headers = {
        'Authorization': f'Api-Key {config.api_key}',
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'madirus',
        'emotion': 'good',
        'folderId': config.folder_id,
    }
    try:
        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code == 200:
            logging.info(f"SPEECHKIT: {resp.content}")
            return True, resp.content

        logging.error(f"SPEECHKIT: Ошибка {resp.text}")
        return False, f"При запросе в SpeechKit возникла ошибка: {resp.text}"
    except Exception as e:
        logging.error(e)
        return e
    
def speech_to_text(data):
    params = "&".join([
        "topic=general",
        f"folderId={config.folder_id}",
        "lang=ru-RU"
    ])

    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}'

    headers = {
        'Authorization': f'Api-Key {config.api_key}',
    }
    try:
        resp = requests.post(url, headers=headers, data=data)
        
        decoded_data = resp.json()
        if decoded_data.get("error_code") is None:
            logging.info("SPEECHKIT: 200 OK")
            return True, decoded_data.get("result")

        logging.error(f"SPEECHKIT: {decoded_data}")
        return False, f"При запросе в SpeechKit возникла ошибка. Текст ошибки: {decoded_data}"
    except Exception as e:
        logging.error(e)
        return e