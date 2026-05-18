from curl_cffi import options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pyperclip
import subprocess
import time


class SeleniumHelper:
    def __init__(self):

        user_data = r"C:\Users\user\selenium_user_data"

        # 크롬 실행 파일 경로 (본인 PC 환경에 맞게 수정)
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        # 파이썬이 CMD 대신 크롬을 직접 실행
        # subprocess.Popen(
        #    [
        #        chrome_path,
        #        f"--remote-debugging-port=9222",
        #        f"--user-data-dir={user_data}",
        #    ]
        # )

        # subprocess.Popen 리스트에 아래 옵션들을 추가
        subprocess.Popen(
            [
                chrome_path,
                "--remote-debugging-port=9222",
                f"--user-data-dir={user_data}",
                "--disable-gpu",  # GPU 가속 끄기 (리소스 절약)
                "--disable-dev-shm-usage",  # 공유 메모리 제한 해제
                "--no-sandbox",  # 보안 샌드박스 비활성화 (안정성 향상)
            ]
        )

        time.sleep(3)

        options = webdriver.ChromeOptions()
        # options.add_argument(f"--user-data-dir={user_data}")

        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        driver = webdriver.Chrome(options=options)

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
        element.send_keys(Keys.CONTROL, "v")

    def wait(self, by, value, timeout=30, click=False):
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        if click:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        return element

    def wait_for_new_window(self, timeout=30, expected_num_of_windows=2):
        WebDriverWait(self.driver, timeout).until(
            EC.number_of_windows_to_be(expected_num_of_windows)
        )
