#import cv2
import glob
#import numpy as np
import os
import pyperclip
import time
import tqdm

from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class NaverPayEventBot:
    def __init__(self):
        self.events = []
        self.click_event_images = []
        #self.load_click_event_images()
        self.set_chrome_driver()
         
    def load_click_event_images(self):
        for path in glob.glob(os.path.join('images', 'click_event_*.png')):
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.click_event_images.append(image)
        
    def set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def paste_safely(self, element, value):
        element.click()
        pyperclip.copy(value)
        #element.send_keys(Keys.CONTROL, 'v') 
        if os.name == 'posix':
            element.send_keys(Keys.COMMAND, 'v') 
        else:
            element.send_keys(Keys.CONTROL, 'v') 

    def login(self, user_id, pw):
        self.set_chrome_driver()
        self.driver.get('https://new-m.pay.naver.com/pcpay/eventbenefit')

        id_element = self.driver.find_element(by=By.ID, value='id')
        self.paste_safely(id_element, user_id)

        pw_element = self.driver.find_element(by=By.ID, value='pw')
        self.paste_safely(pw_element, pw)

        self.driver.find_element(by=By.ID, value='log.login').click()

    def is_click_event(self, img):
        for template in self.click_event_images:
            result = cv2.matchTemplate(img, template, cv2.cv2.TM_SQDIFF_NORMED)
            box_loc = np.where(result < 1e-2)

            if len(box_loc[0]) > 0:
                return True
        
        return False

    def click_onetime_events(self):
        if len(self.events) == 0:
            for _ in range(5):
                self.driver.find_elements(by=By.TAG_NAME, value='body')[0].send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)

            elements = self.driver.find_elements(by=By.CLASS_NAME, value='ADRewardList_banner__2CWl0')
            print(f'Found {len(elements)} elements')
            time.sleep(5)
            #for idx, element in enumerate(tqdm.tqdm(elements, desc='Finding events')):
            for idx, element in enumerate(elements):
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


                    continue

                    try:
                        title_element = element.find_element(by=By.CLASS_NAME, value='title')
                        title = title_element.text
                        is_image_banner = False
                    except:
                        title = "IMAGE BANNER"
                        is_image_banner = True

                    if is_image_banner is False:
                        link_element = element.find_element(by=By.CLASS_NAME, value='type_system')
                    else:
                        link_element = element.find_element(by=By.CLASS_NAME, value='type_image')

                    res = request.urlopen(banner_element.get_attribute('src')).read()
                    img = cv2.imdecode(np.fromstring(res, dtype=np.uint8), cv2.IMREAD_COLOR)
                    url = link_element.get_attribute('href')

                    #print(title)
                    if self.is_click_event(img):
                        self.events.append((title, url))

                except Exception as e:
                    print(str(e))
                    pass

        for title, url in self.events:
            print(f'Click {title} {url}')

            try:
                self.driver.get(url)
            except:
                pass

            time.sleep(3)

    def click_daily_events(self):
        for url in open('event_urls.txt'):
            print(f'trying {url}')
            try:
                self.driver.get(url)
            except:
                pass
            time.sleep(3)

            try:
                self.driver.find_element(by=By.CLASS_NAME, value='call_to_action').click()
            except:
                pass

            time.sleep(1)
    
