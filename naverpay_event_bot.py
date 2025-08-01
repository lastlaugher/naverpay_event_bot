import os
import time
import datetime
import tqdm
import dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_helper import SeleniumHelper

from tinydb import TinyDB, Query

from telegram_helper import send_message
from telegram_server import TelegramServer


class NaverPayEventBot:
    def __init__(self):
        self.url = "https://new-m.pay.naver.com/pcpay/eventbenefit"
        self.selenium = SeleniumHelper()
        self.db = TinyDB("db.json")
        self.telegram_server = None

        self.debug = False
        
    def login(self, user_id, pw):
        self.selenium().get(self.url)

        id_element = self.selenium().find_element(by=By.ID, value="id")
        self.selenium.paste_text_safely(id_element, user_id)

        time.sleep(1)

        pw_element = self.selenium().find_element(by=By.ID, value="pw")
        self.selenium.paste_text_safely(pw_element, pw)

        time.sleep(1)
        self.selenium().find_element(by=By.ID, value="submit_btn").click()

        time.sleep(3)

    def set_telegram(self, token, chat_id):
        self.telegram_token = token
        self.telegram_chat_id = chat_id
        self.telegram_server = TelegramServer(token=token, master_chat_id=chat_id)

    def decide_url(self, refer, current):
        if current.startswith("https://campaign2"):
            end_str = "&request_id"
            idx = current.find(end_str)
            return current[:idx]
        elif refer.startswith("https://campaign2"):
            end_str = "&request_id"
            idx = refer.find(end_str)
            return refer[:idx]
        elif current.startswith("https://ofw.adison.co"):
            return current
        else:
            return None

    def click_onetime_events(self):
        telegram_message = "네이버페이 폐지줍기\n"

        self.selenium().get(self.url)

        try:
            self.selenium.wait(by=By.CLASS_NAME, value="pc-main_panel__GGtFa")
        except:
            if self.telegram_server:
                self.telegram_server.send_message_to_master("로그인 실패")
                os.exit()

        self.selenium().get("https://point.pay.naver.com/pc/mission-detail")
        try:
            self.selenium.wait(
                by=By.CLASS_NAME, value="FlexibleLayout-module_article__bwPeF"
            )
        except:
            if self.telegram_server:
                self.telegram_server.send_message_to_master("클릭 페이지 로딩 실패")
                os.exit()

        for _ in range(10):
            self.selenium().find_elements(by=By.TAG_NAME, value="body")[0].send_keys(
                Keys.PAGE_DOWN
            )
            time.sleep(0.5)

        elements = self.selenium().find_elements(
            by=By.CLASS_NAME, value="BenefitList_item__iYazm"
        )
        print(f"Found {len(elements)} elements")
        time.sleep(5)
        for idx, element in enumerate(tqdm.tqdm(elements, desc="Finding events")):
            try:
                title_element = element.find_elements(
                    by=By.CLASS_NAME, value="DetailItem_description__TUatR"
                )

                if len(title_element) == 0:
                    title = "이미지 배너"
                else:
                    title = title_element[0].text

                reward_element = element.find_elements(
                    by=By.CLASS_NAME, value="DetailItem_badge__ppzfA"
                )

                if len(reward_element) == 0:
                    continue

                reward = reward_element[0].get_attribute("innerText")
                reward = reward.replace("클릭\n", "")
                print(f"{idx} {title} {reward}")

                window_handle_count = len(self.selenium().window_handles)
                try:
                    self.selenium().execute_script(
                        "arguments[0].scrollIntoView(true);", element
                    )
                    anchor = element.find_elements(by=By.TAG_NAME, value="a")[0]
                    self.selenium().execute_script("arguments[0].click();", anchor)

                except Exception as e:
                    pass

                try:
                    self.selenium.wait_for_new_window(
                        timeout=3, expected_num_of_windows=window_handle_count + 1
                    )
                except Exception as e:
                    # 가끔 timeout 이 발생하는 경우가 있어서 무시함
                    pass

                self.selenium().switch_to.window(self.selenium().window_handles[-1])
                time.sleep(1)

                try:
                    popup = self.selenium().find_elements(
                        by=By.CLASS_NAME, value="popup_link"
                    )
                    if popup and len(popup) > 0:
                        popup[0].click()
                except:
                    pass

                time.sleep(1)

                try:
                    self.selenium().switch_to.alert.accept()
                    time.sleep(3)
                except Exception as e:
                    pass

                refer_url = self.selenium().execute_script("return document.referrer")
                url = self.decide_url(refer_url, self.selenium().current_url)
                print(url)

                if not self.debug and url and not self.db.search(Query().url == url):
                    self.db.insert(
                        {
                            "url": url,
                            "title": title,
                            "reward": reward,
                            "time": str(datetime.datetime.now()),
                        }
                    )

                    telegram_message += f"{title} {reward}\n{url}\n\n"

                time.sleep(3)
                self.selenium().close()
                self.selenium().switch_to.window(self.selenium().window_handles[0])

            except Exception as e:
                print(str(e))
                send_message(
                    self.telegram_token,
                    self.telegram_chat_id,
                    "exception occurred in naverpaybot: " + str(e),
                )
                exit()

        if not self.debug and self.telegram_server:
            self.telegram_server.broadcast(telegram_message)


if __name__ == "__main__":
    dotenv.load_dotenv()
    bot = NaverPayEventBot()

    user_id = os.getenv("naver_id")
    pw = os.getenv("naver_pw")
    telegram_token = os.getenv("telegram_token")
    telegram_chat_id = os.getenv("telegram_chat_id")

    print(f"login with {user_id}")
    bot.login(user_id, pw)

    if telegram_token:
        print(f"set telegram with token {telegram_token}")
        bot.set_telegram(telegram_token, telegram_chat_id)

    bot.click_onetime_events()
