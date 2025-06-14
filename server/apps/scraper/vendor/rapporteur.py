import requests


class TelegramReporter(object):
    def __init__(self, tg_token):
        self.tg_token = tg_token

    def send_document(self, chat_id, file_path, caption):
        try:
            file = {'document': open(file_path, 'rb')}
            data = {'chat_id': chat_id,
                    'caption': caption,
                    'parse_mode': 'html',
                    'disable_notification': True}
            url = f'https://api.telegram.org/bot{self.tg_token}/sendDocument'
            response = requests.post(url, files=file, data=data, timeout=10)
            if response:
                print(f"{file_path} отправлен в телеграм")
        except Exception as ex:
            print(f"Не удалось отправить {file_path}: {ex}")

    def send_error_message(self, chat_id, text):
        try:
            data = {'chat_id': chat_id,
                    'text': text,
                    'parse_mode': 'html',
                    'disable_notification': True}
            url = f'https://api.telegram.org/bot{self.tg_token}/sendMessage'
            response = requests.post(url, data, timeout=10)
            if response:
                print(f"Сообщение об ошибке отправлено в телеграм")
        except Exception as ex:
            print(f"Не удалось отправить сообщение об ошибке: {ex}")
