import time

from naverpay_event_bot import NaverPayEventBot

def main():

    bot = NaverPayEventBot()

    for account in open('accounts.txt'):
        user_id = account.split('/')[0]
        pw = account.split('/')[1]

        print(f'login with {user_id}')

        bot.login(user_id, pw)
        bot.click_onetime_events()
        bot.click_daily_events()

        time.sleep(3)

if __name__ == '__main__':
    main()
