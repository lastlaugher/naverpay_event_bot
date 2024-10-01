import os
import time
import datetime

import dotenv
import telegram
from tinydb import TinyDB, Query

class TelegramServer:
    def __init__(self, token, master_chat_id):
        self.token = token
        self.master_chat_id = master_chat_id
        self.bot = telegram.Bot(token=token)
        self.db = TinyDB('subscriber.json')

    def listen(self):
        while True:
            self.poll()
            time.sleep(1)

    def poll(self):
        for item in self.bot.getUpdates():
            chat_id = item.message.chat.id

            if not self.exists(chat_id):
                self.add_user(item.message.chat.to_dict())
                self.send_message(chat_id=chat_id, message=f'{item.message.chat.last_name} {item.message.chat.first_name} 님 환영합니다.')
                self.send_message_to_master(message=f'{item.message.chat.last_name} {item.message.chat.first_name} ({chat_id}) 님이 가입했습니다.')

    def add_user(self, item:dict):
        item['time'] = str(datetime.datetime.now())
        self.db.insert(item)

    def exists(self, chat_id) -> bool:
        return self.db.search(Query().id == chat_id)

    def broadcast(self, message:str):
        for item in self.db.all():
            try:
                last_name = ''
                if 'last_name' in item:
                    last_name = item['last_name']

                first_name = ''
                if 'first_name' in item:
                    first_name = item['first_name']

                self.send_message(item['id'], message)
                self.send_message_to_master(f'{item["id"]} {last_name} {first_name} 전송 완료')
            except Exception as e:
                self.send_message_to_master(f'{item["id"]} {last_name} {first_name} 전송 실패 {str(e)}')

    def send_message(self, chat_id:str, message:str):
        self.bot.sendMessage(chat_id=chat_id, text=message)

    def send_message_to_master(self, message):
        self.send_message(chat_id=self.master_chat_id, message=message)

if __name__ == '__main__':
    dotenv.load_dotenv()

    token = os.getenv('telegram_token')
    chat_id = os.getenv('telegram_chat_id')

    if not token:
        raise Exception('telegram_token is not set')

    if not chat_id:
        raise Exception('telegram_chat_id is not set')

    server = TelegramServer(token=token, master_chat_id=chat_id)
    server.poll()