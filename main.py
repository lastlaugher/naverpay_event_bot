import time

from naverpay_event_bot import NaverPayEventBot, Message

def main():

    bot = NaverPayEventBot()

    for account in open('accounts.txt'):
        tokens = account.split('/')

        user_id = tokens[0]
        pw = tokens[1]

        if len(tokens) > 2:
            telegram_token  = tokens[2]
            telegram_chat_id = tokens[3]

        print(f'login with {user_id}')

        bot.login(user_id, pw)
        bot.set_telegram(telegram_token, telegram_chat_id)

        message = Message()
        bot.click_onetime_events(message)

        time.sleep(3)

if __name__ == '__main__':
    main()
