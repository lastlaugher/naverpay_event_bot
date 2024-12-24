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
        self.subscriber_db = TinyDB('subscriber.json')
        self.message_db = TinyDB('message.json')

    def listen(self):
        while True:
            self.poll()
            time.sleep(1)

    def poll(self):
        for item in self.bot.getUpdates():
            if not item.message:
                continue

            chat_id = item.message.chat.id

            if not self.exists(chat_id, 'user'):
                self.add_user(item.message.chat.to_dict())
                self.send_message(chat_id=chat_id, message=f'{item.message.chat.last_name} {item.message.chat.first_name} 님 네이버 폐지 줍줍에 가입하신 것을 환영합니다.')
                self.send_message_to_master(message=f'{item.message.chat.last_name} {item.message.chat.first_name} ({chat_id}) 님이 가입했습니다.')

            message_id = item.message.message_id
            if not self.exists(message_id, 'message'):
                self.add_message(item.message.to_dict())
                self.send_message_to_master(message=f'{item.message.chat.last_name} {item.message.chat.first_name} 님이 메시지를 전송했습니다.\n{item.message.text}')

    def add_user(self, item:dict):
        item['time'] = str(datetime.datetime.now())
        self.subscriber_db.insert(item)

    def add_message(self, item:dict):
        item['time'] = str(datetime.datetime.now())
        self.message_db.insert(item)

    def exists(self, id, type:str) -> bool:
        if type == "user":
            return self.subscriber_db.search(Query().id == id)
        elif type == "message":
            return self.message_db.search(Query().message_id == id)
        else:
            raise Exception(f'Unspoorted type: {type}')

    def broadcast(self, message:str):
        for item in self.subscriber_db.all():
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
    #server.broadcast('[공지] 그동안 매주 월요일 9시에 크롤링을 해서 전송했는데, 그렇게 하면 놓치는 줍줍이 있다는 제보가 들어왔습니다.\n그래서 앞으로는 월, 목 오전 9시에 전송할 예정입니다.\n개선 요청은 언제든지 환영합니다.\n감사합니다.\n주인백')