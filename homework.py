import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HW_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HW_STATUS = {
        'reviewing': 'работа взята в ревью',
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось, '
        'можно приступать к следующему уроку.'
    }


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('Данные по новому проекту отсутствуют', exc_info=True)
    if homework.get('status') is None:
        logging.error('Статус отсутствует', exc_info=True)
    elif homework.get('status') == 'reviewing':
        verdict = HW_STATUS['reviewing']
    elif homework.get('status') == 'rejected':
        verdict = HW_STATUS['rejected']
    else:
        verdict = HW_STATUS['approved']
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            HW_URL,
            params=params,
            headers=headers
        )
    except requests.RequestException as error:
        logging.error(error, exc_info=True)
    return homework_statuses.json()


def send_message(message, bot_client):
    try:
        return bot_client.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f'Возникла неизвестная ошибка бота {e}')


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - 1849000
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                logging.info('Бот отправил сообщение')
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
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
