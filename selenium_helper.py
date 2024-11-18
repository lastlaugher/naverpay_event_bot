
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pyperclip

class SeleniumHelper:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=chrome_options)

        self.driver = driver

    def get(self, url):
        self.driver.get(url)

    def __call__(self):
        return self.driver

    def enter_text(self, element_id, text, by_name=False):
        if by_name:
            element = self.driver.find_elements(by=By.NAME, value=element_id)[0]
        else:
            element = self.driver.find_element(by=By.ID, value=element_id)
        element.send_keys(text)

    def paste_text_safely(self, element, value):
        element.click()
        pyperclip.copy(value)
        element.send_keys(Keys.CONTROL, 'v') 

    def wait(self, by, value, timeout=30, click=False):
        element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        if (click):
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))
        return element

    def wait_for_new_window(self, timeout=30, expected_num_of_windows=2):
        WebDriverWait(self.driver, timeout).until(EC.number_of_windows_to_be(expected_num_of_windows))