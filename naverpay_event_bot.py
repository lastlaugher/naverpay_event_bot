import os
import time
import datetime
import random
import tqdm
import dotenv

from DrissionPage import ChromiumPage, ChromiumOptions
from tinydb import TinyDB, Query

from telegram_helper import send_message
from telegram_server import TelegramServer


class NaverPayEventBot:
    def __init__(self):
        self.url = "https://new-m.pay.naver.com/pcpay/eventbenefit"

        co = ChromiumOptions()
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-save-password-bubble")
        self.page = ChromiumPage(co)

        self.db = TinyDB("db.json")
        self.telegram_server = None
        self.telegram_token = None
        self.telegram_chat_id = None
        self.debug = False

    def login(self, user_id, pw):
        self.page.get("https://nid.naver.com/nidlogin.login")
        self.page.wait.load_start()

        if not self.page.ele("#id"):
            print("Already logged in")
            return

        self.page.ele("#id").input(user_id)
        time.sleep(0.8)
        self.page.ele("#pw").input(pw)
        time.sleep(1.2)

        login_btn = self.page.ele("#log.login") or self.page.ele("@value=로그인")
        login_btn.click()

        self.page.wait.load_start()
        time.sleep(2)
        print(f"로그인 후 현재 페이지: {self.page.title}")

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

        self.page.get("https://point.pay.naver.com/pc/mission-detail")
        time.sleep(8)
        print(f"mission-detail 페이지 로딩: {self.page.url}")

        if not self.page.run_js(
            "return !!document.querySelector('.FlexibleLayout-module_article__bwPeF')"
        ):
            print("미션 페이지 로딩 실패 - 타이틀:", self.page.title)
            if self.telegram_server:
                self.telegram_server.send_message_to_master(
                    "미션 페이지 로딩 실패 (로그인 확인)"
                )
            return

        for _ in range(10):
            self.page.run_js("window.scrollBy(0, 300)")
            time.sleep(0.5)

        elements = self.page.eles(".BenefitList-module-scss-module__wOuXPq__item")
        print(f"Found {len(elements)} elements")
        time.sleep(5)

        for idx, element in enumerate(tqdm.tqdm(elements, desc="Finding events")):
            try:
                title_element = element.eles(
                    ".DetailItem-module-scss-module__YUdvEa__description"
                )
                title = title_element[0].text if title_element else "이미지 배너"

                reward_element = element.eles(
                    ".DetailItem-module-scss-module__YUdvEa__badge"
                )
                if not reward_element:
                    continue

                reward = reward_element[0].text.replace("클릭", "").strip()
                print(f"{idx} {title} {reward}")

                anchor = element.ele("tag:a")
                if not anchor:
                    continue

                main_tab_id = self.page.tab_id
                before_tab_ids = set(self.page.tab_ids)

                element.scroll.to_see()
                time.sleep(random.uniform(0.5, 1.0))
                anchor.click()

                time.sleep(3)

                after_tab_ids = set(self.page.tab_ids)
                new_tab_ids = list(after_tab_ids - before_tab_ids)

                if new_tab_ids:
                    new_tab = self.page.get_tab(new_tab_ids[-1])
                    time.sleep(1)

                    try:
                        popup = new_tab.ele(".popup_link", timeout=2)
                        if popup:
                            popup.click()
                    except Exception:
                        pass

                    time.sleep(1)

                    try:
                        new_tab.handle_alert(accept=True, timeout=2)
                        time.sleep(3)
                    except Exception:
                        pass

                    try:
                        refer_url = new_tab.run_js("return document.referrer")
                        url = self.decide_url(refer_url, new_tab.url)
                    except Exception:
                        url = None
                    print(url)

                    if (
                        not self.debug
                        and url
                        and not self.db.search(Query().url == url)
                    ):
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
                    new_tab.close()
                    self.page.activate_tab(main_tab_id)
                else:
                    # 새 탭 없이 같은 탭에서 열린 경우
                    time.sleep(1)
                    refer_url = self.page.run_js("return document.referrer")
                    url = self.decide_url(refer_url, self.page.url)
                    print(url)

                    if (
                        not self.debug
                        and url
                        and not self.db.search(Query().url == url)
                    ):
                        telegram_message += f"{title} {reward}\n{url}\n\n"

            except Exception as e:
                err_msg = repr(e)
                print(f"이벤트 {idx} 처리 오류: {err_msg}")
                try:
                    self.page.activate_tab(main_tab_id)
                except Exception:
                    pass

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
    bot.page.quit()
