import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HW_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname, %(name)s, %(message)s)s')


def parse_homework_status(homework):
    homework_name = HW_URL.get('homework_name')
    homework = 
    if HW_URL.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework_name == 'approved':
        verdict = 'Ревьюеру всё понравилось,'
        'можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    homework_statuses = requests.get(HW_URL, params=params, headers=headers)
    try:
        homework_statuses.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logging.error(error, exc_info=True)
    return homework_statuses.json()


def send_message(message, bot_client):
    message = parse_homework_status()
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token='TELEGRAM_TOKEN')
    current_timestamp = int(time.time()) - 2592000
    #1607604245

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
