from DrissionPage import ChromiumPage, ChromiumOptions
import time


class NaverBot:
    def __init__(self):
        # 1. 브라우저 옵션 설정
        co = ChromiumOptions()

        # [변경] user_data 설정을 하지 않으면 임시 프로필로 실행됩니다.
        # 대신, 봇 탐지를 피하기 위한 기본 최적화 설정을 추가합니다.
        co.set_argument("--no-sandbox")  # 리소스 제한 완화
        co.set_argument("--disable-gpu")  # 안정성 향상

        # 2. 브라우저 실행
        self.page = ChromiumPage(co)

    def login(self, user_id, pw):
        # 네이버 로그인 페이지 접속
        self.page.get("https://nid.naver.com/nidlogin.login")

        # 페이지 로딩 대기
        self.page.wait.load_start()

        # 이미 로그인된 상태인지 체크 (아이디 입력창이 없는 경우)
        if not self.page.ele("#id"):
            print("로그인 페이지에 접근할 수 없거나 이미 로그인 상태입니다.")
            return

        # 3. 아이디 입력 (DrissionPage는 실제 클립보드 복사-붙여넣기 처럼 동작함)
        # s_typing=True 옵션을 주면 더 인간적인 속도로 입력합니다.
        self.page.ele("#id").input(user_id)
        time.sleep(0.8)

        # 4. 비밀번호 입력
        self.page.ele("#pw").input(pw)
        time.sleep(1.2)

        # 5. 로그인 버튼 클릭
        # 네이버 로그인 버튼의 ID는 'log.login'인데 점(.)이 포함되어 있어
        # 셀렉터에서 백슬래시(\)로 이스케이프 처리가 필요할 수 있습니다.
        login_btn = self.page.ele("#log.login") or self.page.ele("@value=로그인")
        login_btn.click()

        # 로그인 처리 후 메인 페이지 이동 대기
        self.page.wait.load_start()
        time.sleep(2)

        print(f"로그인 시도 후 현재 페이지: {self.page.title}")


# 실행
bot = NaverBot()
bot.login("tech0816", "")
