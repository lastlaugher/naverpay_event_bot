from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

import cv2
import pyperclip
import numpy as np
import glob
import tqdm

class NaverPayEventBot:
    def __init__(self):
        self.events = []
        self.click_event_images = []
        self.load_click_event_images()
        self.set_chrome_driver()
         
    def get_roi_image(self, image):
        roi_x = 30
        roi_y = 32
        roi_w = 84
        roi_h = 78

        return image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

    def load_click_event_images(self):
        for path in glob.glob('click_event_*.png'):
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            roi_image = self.get_roi_image(image)
            self.click_event_images.append(roi_image)
        
    def set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def paste_safely(self, element, value):
        element.click()
        pyperclip.copy(value)
        element.send_keys(Keys.CONTROL, 'v') 

    def login(self, user_id, pw):
        self.set_chrome_driver()
        self.driver.get('https://event2.pay.naver.com/event/benefit/list')

        id_element = self.driver.find_element(by=By.ID, value='id')
        self.paste_safely(id_element, user_id)

        pw_element = self.driver.find_element(by=By.ID, value='pw')
        self.paste_safely(pw_element, pw)

        self.driver.find_element(by=By.ID, value='log.login').click()

    def is_click_event(self, img):
        roi_img = self.get_roi_image(img)

        for template in self.click_event_images:
            diff = np.abs(template - roi_img)
            match_count = np.count_nonzero(diff < 5)
            #print(f'score: {match_count}')
            if match_count > roi_img.shape[0] * roi_img.shape[1] * 3 * 0.9:
                return True
        
        return False

    def click_onetime_events(self):
        if len(self.events) == 0:
            elements = self.driver.find_elements(by=By.CLASS_NAME, value='event_area')
            for element in tqdm.tqdm(elements, desc='Finding events'):
                try:
                    banner_element = element.find_element(by=By.CLASS_NAME, value='banner')
                    title_element = element.find_element(by=By.CLASS_NAME, value='title')
                    link_element = element.find_element(by=By.CLASS_NAME, value='type_system')

                    res = request.urlopen(banner_element.get_attribute('src')).read()
                    img = cv2.imdecode(np.fromstring(res, dtype=np.uint8), cv2.IMREAD_COLOR)
                    url = link_element.get_attribute('href')

                    #print(title_element.text)
                    if self.is_click_event(img):
                        self.events.append((title_element.text, url))

                except Exception as e:
                    pass

        for title, url in self.events:
            print(f'Click {title} {url}')

            try:
                self.driver.get(url)
            except:
                pass

            sleep(3)

    def click_daily_events(self):
        for url in open('event_urls.txt'):
            print(f'trying {url}')
            self.driver.get(url)
            sleep(3)

            try:
                self.driver.find_element(by=By.CLASS_NAME, value='call_to_action').click()
            except:
                pass

            sleep(1)
    
