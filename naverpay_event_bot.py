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
        
    def click_onetime_events(self, message:Message):
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
                    title_element = element.find_elements(by=By.CLASS_NAME, value='ADRewardBannerSystem_title__3f6bG')

                    if len(title_element) == 0:
                        title = '이미지 배너'
                    else:
                        title = title_element[0].text

                    reward_element = element.find_elements(by=By.CLASS_NAME, value='ADRewardBadgeClick_hide__2QRl2')

                    if len(reward_element) == 0:
                        continue

                    reward = reward_element[1].get_attribute('innerText')
                    print(f'{idx} {title} {reward}')

                    element.click()

                    self.selenium.wait_for_new_window()
                    self.selenium().switch_to.window(self.selenium().window_handles[-1])

                    url = self.selenium().current_url
                    end_str = 'DETAIL_FROM_LIST'
                    idx = url.find(end_str)
                    url = url[:idx + len(end_str)]

                    print(url)

                    if not self.db.search(Query().url == url):
                        self.db.insert({'url': url})

                        if self.telegram_token:
                            send_message(self.telegram_token, self.telegram_chat_id, f'NEW NAVERPAY REWARD\n{url}')

                    time.sleep(1)

                    try:
                        self.selenium().switch_to.alert.accept()
                    except:
                        pass

                    self.selenium().close()
                    self.selenium().switch_to.window(self.selenium().window_handles[0])

                except Exception as e:
                    print(str(e))