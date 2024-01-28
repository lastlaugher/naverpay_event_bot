import cv2
import glob
import numpy as np
import os
import time
import tqdm

from urllib import request

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_helper import SeleniumHelper

class Message:
    def __init__(self):
        self.text = ""
        self.progress = 0   # 0 - 100
        
class NaverPayEventBot:
    def __init__(self):
        self.url ='https://new-m.pay.naver.com/pcpay/eventbenefit'
        self.events = []
        self.click_event_images = []
        self.selenium = SeleniumHelper()
        self.load_click_event_images()
        self.debug = False
         
    def load_click_event_images(self):
        for path in glob.glob(os.path.join('images', 'click_event_*.png')):
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.click_event_images.append(image)
        
    def login(self, user_id, pw):
        self.selenium().get(self.url)

        id_element = self.selenium().find_element(by=By.ID, value='id')
        self.selenium.paste_text_safely(id_element, user_id)

        time.sleep(1)

        pw_element = self.selenium().find_element(by=By.ID, value='pw')
        self.selenium.paste_text_safely(pw_element, pw)

        time.sleep(1)
        self.selenium().find_element(by=By.ID, value='log.login').click()

    def is_click_event(self, img):
        for template in self.click_event_images:
            result = cv2.matchTemplate(img, template, cv2.cv2.TM_SQDIFF_NORMED)
            box_loc = np.where(result < 1e-2)

            if self.debug:
                print(box_loc)

            if len(box_loc[0]) > 0:
                return True
        
        return False

    def click_onetime_events(self, message:Message):
        self.selenium().get(self.url)

        self.selenium.wait(by=By.TAG_NAME, value='body')
        if len(self.events) == 0:
            for _ in range(0, 5): 
                self.selenium().find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)

            #elements = self.selenium().find_elements(by=By.XPATH, value='/html/body/div/div/div[2]/div/div/div[4]/div[3]/div/div/div/ul/li')
            elements = self.selenium().find_elements(by=By.CLASS_NAME, value='ADRewardList_banner__2CWl0')
            message.text = f'총 {len(elements)} 개의 이벤트를 찾았습니다.'
            time.sleep(5)
            for idx, element in enumerate(tqdm.tqdm(elements, desc='Finding events')):
                message.progress = (idx + 1) / len(elements) * 100
                try:
                    reward_element = element.find_element(by=By.CLASS_NAME, value='ADRewardBadgeClick_hide__2QRl2')

                    print(f'{idx} {reward_element.text}')

                    banner_element = element.find_element(by=By.CLASS_NAME, value='banner')

                    try:
                        title_element = element.find_element(by=By.CLASS_NAME, value='title')
                        title = title_element.text
                        is_image_banner = False
                    except:
                        title = f'이미지 배너 {len(self.events) + 1}'
                        is_image_banner = True

                    if is_image_banner is False:
                        link_element = element.find_element(by=By.CLASS_NAME, value='type_system')
                    else:
                        link_element = element.find_element(by=By.CLASS_NAME, value='type_image')

                    res = request.urlopen(banner_element.get_attribute('src')).read()
                    img = cv2.imdecode(np.fromstring(res, dtype=np.uint8), cv2.IMREAD_COLOR)
                    url = link_element.get_attribute('href')

                    message.text = f'{title} 분석중...'

                    if self.debug:
                        print(title)

                    if self.is_click_event(img):
                        self.events.append((title, url))

                except Exception as e:
                    pass

        for title, url in self.events:
            if self.debug:
                print(f'Click {title} {url}')

            message.text = f'{title} 클릭...'

            try:
                self.selenium().get(url)
            except:
                pass

            time.sleep(5)

    def click_daily_events(self, event_list, message:Message):
        message.text = f'{len(event_list)} 개의 이벤트를 시도합니다.'
        message.progress = 0
        
        for idx, (name, url, _) in enumerate(event_list):
            message.text = f'{name} 클릭...'
            message.progress = (idx + 1) / len(event_list) * 100
            try:
                self.selenium().get(url)
            except:
                pass
            time.sleep(3)

            try:
                self.selenium().find_element(by=By.CLASS_NAME, value='call_to_action').click()
            except:
                pass

            time.sleep(1)
    
