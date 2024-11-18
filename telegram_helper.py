import os
import dotenv
import telegram

def get_chat_id(token):
    bot = telegram.Bot(token=token)
    if len(bot.getUpdates()) == 0:
        raise Exception('Can\'t get chat id. Please check if the token is valid or retry after sending a message to the bot')
    
    return bot.getUpdates()[-1].message.chat.id

def send_message(token, chat_id, message):
    bot = telegram.Bot(token=token)

    tokens = split_message(message)

    for token in tokens:
        bot.sendMessage(chat_id=chat_id, text=token)

def split_message(message):
    messages = []
    max_length = 4096

    while True:
        if len(message) < max_length:
            messages.append(message)
            break
    
        idx = message.rfind('\n', max_length)
        messages.append(message[:idx])

        message = message[idx+1:]

    return messages

if __name__ == '__main__':
    dotenv.load_dotenv()
    token = os.getenv('telegram_token')

    chat_id = get_chat_id(token)
    print(f'chat_id: {chat_id}')
    send_message(token, chat_id, '테스트 메시지')