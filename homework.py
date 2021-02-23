import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)
handler.setFormatter(formatter)

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HOMEWORK_STATUSES = {
    'reviewing': 'работа взята в ревью',
    'approved':
        'Ревьюеру всё понравилось, можно приступать к следующему уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
}
HOMEWORK_REVIEW = 'У вас проверили работу "{arg_name}"!\n\n{arg_status}'


def parse_homework_status(homework):
    if homework is None:
        message = 'Проблемы с ответом от сервера.'
        logger.error(message, exc_info=True)
        return dict()
    else:
        homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return HOMEWORK_REVIEW.format(
            arg_name=homework_name, arg_status=verdict
        )
    else:
        raise KeyError('Неизвестный статус!')


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(
            URL_API, headers=headers, params=params
        )
        return homework_statuses.json()
    except requests.exceptions.HTTPError as err_http:
        logger.exception(err_http)
        raise err_http
    except requests.RequestException as error:
        logger.exception(error)
        raise error


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = Bot(TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        logger.debug('Запуск telegram бота')
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client
                )
                logger.info('Отправлено сообщение в чат Telegram.')
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(300)
        except Exception as error:
            logger.exception(error)
            send_message(error, bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
