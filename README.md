# python package 설치
```bash
pip install -r requirements.txt
```

# .env 파일 생성
clone 받은 경로에 .env 파일을 생성해서 아래의 내용을 입력한다.
```
telegram_token=텔레그램 토큰 입력
telegram_chat_id=아래 단계에서 얻은 값을 입력
naver_id=네이버 아이디
naver_pw=네이버 암호
```

# 텔레그램 chat id 얻기
```
python telegram_helper.py
```
여기서 얻은 값을 .env 파일에 추가한다.

# 실행하기
```
python naverpay_event_bot.py
```
