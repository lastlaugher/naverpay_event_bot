import time
import tqdm

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_helper import SeleniumHelper

from tinydb import TinyDB, Query

from telegram_helper import send_message

class Message:
    def __init__(self):
        self.text = ""
        self.progress = 0   # 0 - 100
        
class NaverPayEventBot:
    def __init__(self):
        self.url ='https://new-m.pay.naver.com/pcpay/eventbenefit'
        self.events = []
        self.selenium = SeleniumHelper()
        self.debug = False
        self.db = TinyDB('db.json')
        self.telegram_token = None
        self.telegram_chat_id = None
         
    def login(self, user_id, pw):
        self.selenium().get(self.url)

        id_element = self.selenium().find_element(by=By.ID, value='id')
        self.selenium.paste_text_safely(id_element, user_id)

        time.sleep(1)

        pw_element = self.selenium().find_element(by=By.ID, value='pw')
        self.selenium.paste_text_safely(pw_element, pw)

        time.sleep(1)
        self.selenium().find_element(by=By.ID, value='log.login').click()

    def set_telegram(self, token, chat_id):
        self.telegram_token = token
        self.telegram_chat_id = chat_id
        
    def decide_url(self, refer, current):
        if refer.startswith('https://campaign2-api'):
            end_str = '&request_id'
            idx = refer.find(end_str)
            return refer[:idx]
        elif current.startswith('https://ofw.adison.co'):
            return current
        else:
            return refer

    def click_onetime_events(self, message:Message):
        telegram_message = '네이버페이 폐지줍기\n'

        self.selenium().get(self.url)

        self.selenium.wait(by=By.TAG_NAME, value='body')
        if len(self.events) == 0:
            for _ in range(5):
                self.selenium().find_elements(by=By.TAG_NAME, value='body')[0].send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)

            elements = self.selenium().find_elements(by=By.CLASS_NAME, value='ADRewardList_banner__2CWl0')
            print(f'Found {len(elements)} elements')
            time.sleep(5)
            for idx, element in enumerate(tqdm.tqdm(elements, desc='Finding events')):
                try:
                    title_element = element.find_elements(by=By.CLASS_NAME, value='ADRewardBannerSystem_description__3c34J')

                    if len(title_element) == 0:
                        title = '이미지 배너'
                    else:
                        title = title_element[0].text

                    reward_element = element.find_elements(by=By.CLASS_NAME, value='ADRewardClickBadge_badge__1xs0W')

                    if len(reward_element) == 0:
                        continue

                    reward = reward_element[0].get_attribute('innerText')
                    reward = reward.replace('클릭', '')
                    print(f'{idx} {title} {reward}')

                    element.click()

                    self.selenium.wait_for_new_window()
                    self.selenium().switch_to.window(self.selenium().window_handles[-1])

                    time.sleep(1)

                    try:
                        self.selenium().switch_to.alert.accept()
                        time.sleep(3)
                    except Exception as e:
                        pass

                    refer_url = self.selenium().execute_script('return document.referrer')
                    url = self.decide_url(refer_url, self.selenium().current_url)
                    print(url)

                    if not self.db.search(Query().url == url):
                        self.db.insert({'url': url, 'title': title, 'reward': reward, 'time': time.time()})

                        telegram_message += f'{title} {reward}\n{url}\n\n'

                    time.sleep(5)
                    self.selenium().close()
                    self.selenium().switch_to.window(self.selenium().window_handles[0])

                except Exception as e:
                    print(str(e))
                    send_message(self.telegram_token, self.telegram_chat_id, 'exception occurred in naverpaybot: ' + str(e))
                    exit()

            if self.telegram_token:
                send_message(self.telegram_token, self.telegram_chat_id, telegram_message)