Бот-асистент для API сервиса Telegram

Эта программа реализует бот-ассистента, который периодично обращается 
к API Яндекс.Практикума - получает данные в формате JSON о статусе 
проверки домашнего задания, формирует из них информационное сообщение, 
передаёт результат в личный Телеграм-чат.

Программа логирует в файл main.log все статусы до уровня DEBUG включительно.

Для реализации Телеграм-бота используется:
   библиотека python-telegram-bot, пакет telegram.
