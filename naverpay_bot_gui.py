import datetime
import threading
import time

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

import crypt
from naverpay_event_bot import NaverPayEventBot, Message
from naverpay_bot_db import NaverPayBotDB

class NaverPayEventPickUp(MDApp):
        
    def build(self):
        self.theme_cls.primary_palette = "Green"
        gui = Builder.load_string(
            '''
BoxLayout:
    orientation:'vertical'
    MDTopAppBar:
        title: 'NaverPay Event Pick-Up'

    MDBottomNavigation:
        MDBottomNavigationItem:
            name: 'home'
            text: 'home'
            icon: 'home'

            StackLayout:
                orientation: 'lr-tb'
                padding: 20

                MDLabel:
                    text: '1회성 클릭 이벤트'
                    font_name: 'NanumGothic.ttf'
                    font_size: 25
                    size_hint: 1.0, 0.1

                MDBoxLayout:
                    size_hint: 1.0, 0.1
                    orientation: 'horizontal'

                    MDLabel:
                        text: '예약시간 12:00'
                        font_name: 'NanumGothic.ttf'

                    MDRaisedButton:
                        text: '지금 실행'
                        font_name: 'NanumGothic.ttf'
                        pos_hint: {"center_y": .5}
                        on_release: app.run_click_event()

                MDProgressBar:
                    id: progress
                    value: 0
                    size_hint: 1.0, 0.05

                MDLabel:
                    id: log
                    text: ''
                    font_name: 'NanumGothic.ttf'
                    size_hint: 1.0, 0.1

                MDLabel:
                    text: '매일 선착순 이벤트'
                    font_name: 'NanumGothic.ttf'
                    font_size: 25
                    size_hint: 1.0, 0.1

                MDBoxLayout:
                    size_hint: 1.0, 0.1
                    orientation: 'horizontal'

                    MDLabel:
                        text: '예약시간 12:00'
                        font_name: 'NanumGothic.ttf'

                    MDRaisedButton:
                        text: '지금 실행'
                        font_name: 'NanumGothic.ttf'
                        pos_hint: {"center_y": .5}
                        on_release: app.run_daily_event()

                MDProgressBar:
                    id: progress
                    value: 0
                    size_hint: 1.0, 0.05

                MDLabel:
                    id: log2
                    text: ''
                    font_name: 'NanumGothic.ttf'
                    size_hint: 1.0, 0.1


        MDBottomNavigationItem:
            name: 'account'
            text: 'account'
            icon: 'account'

            StackLayout:
                orientation: 'lr-tb'
                padding: 30

                MDLabel:
                    text: 'Naver 계정을 입력하세요 (암호화해서 저장하므로 안심하세요)'
                    font_name: 'NanumGothic.ttf'
                    size_hint: 1.0, None

                MDTextField:
                    hint_text: 'ID'
                    size_hint: 1.0, None
                    id: id

                MDTextField:
                    hint_text: 'Password'
                    password: 'true'
                    size_hint: 1.0, None
                    id: pw

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1.0, None

                    MDRaisedButton:
                        text: '저장'
                        font_name: 'NanumGothic.ttf'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.save_db()
                
        MDBottomNavigationItem:
            name: 'Settings'
            text: 'Settings'
            icon: 'cog'

            StackLayout:
                orientation: 'lr-tb'
                padding: 30

                MDLabel:
                    text: '1회성 클릭 이벤트 실행 시간'
                    font_name: 'NanumGothic.ttf'
                    font_size: 25
                    size_hint: 1.0, 0.1

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1.0, 0.1

                    MDLabel:
                        text: '예약 시간'
                        font_name: 'NanumGothic.ttf'

                    MDLabel:
                        text: '00:00'
                        font_name: 'NanumGothic.ttf'
                        id: schedule

                    BoxLayout:
                    BoxLayout:
                    BoxLayout:

                    MDRaisedButton:
                        text: '설정'
                        font_name: 'NanumGothic.ttf'
                        on_release: app.show_time_picker()
                        pos_hint: {"center_y": .5}

                MDLabel:
                    text: '매일 선착순 이벤트 목록'
                    font_name: 'NanumGothic.ttf'
                    font_size: 25
                    size_hint: 1.0, None

                BoxLayout:
                    id: table
                    size_hint: 1.0, 0.5

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1.0, 0.05
                    pos_hint: {"center_x": .5}

                    MDRaisedButton:
                        text: '삭제'
                        font_name: 'NanumGothic.ttf'
                        pos_hint: {"center_x": .5, "center_y": .5}
                        on_release: app.delete_event()

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1.0, 0.1
                    spacing: 10
                   
                    MDTextField:
                        hint_text: '이름'
                        size_hint: 0.2, None
                        id: event_name
                   
                    MDTextField:
                        hint_text: 'URL'
                        size_hint: 0.4, None
                        id: event_url
                   
                    MDTextField:
                        hint_text: '시간'
                        size_hint: 0.1, None
                        id: event_schedule

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1.0, 0.05

                    MDRaisedButton:
                        text: '추가'
                        font_name: 'NanumGothic.ttf'
                        pos_hint: {"center_x": .5, "center_y": .5}
                        on_release: app.add_event()
'''
        )

        self.daily_event_data_tables = MDDataTable(
            rows_num=20,
            check=True,
            column_data=[
                ("[font=NanumGothic.ttf]이름[/font]", dp(40)),
                ("URL", dp(85)),
                ("[font=NanumGothic.ttf]실행 시간[/font]", dp(15)),
            ],
            elevation=2,
        )

        self.daily_event_data_tables.bind(on_check_press=self.on_check_press)

        Window.size = (800, 1000)
         
        return gui

    def on_start(self):
        self.db = NaverPayBotDB()
        self.load_db()

        self.root.ids.table.add_widget(self.daily_event_data_tables)
        self.delete_candidates = []

        Clock.schedule_interval(self.check_event_time, 5)

        self.thread = None
        
    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.set_time)

        time_obj = datetime.datetime.strptime(f"{self.root.ids.schedule.text}:00", "%H:%M:%S")

        time_dialog.set_time(time_obj)
        time_dialog.open()

    def set_time(self, instance, time):
        # convert HH:MM:SS to HH:MM
        self.root.ids.schedule.text = f'{time.hour:02d}:{time.minute:02d}'
    
    def run_daily_event(self):
        self.run_thread(mode='daily')
    
    def run_onetime_event(self):
        self.run_thread(mode='onetime')
       
    def close_dialog(self, obj):
        self.dialog.dismiss()
            
    def run_thread(self, mode):
        if len(self.root.ids.id.text) == 0 or len(self.root.ids.pw.text) == 0:
            self.dialog = MDDialog(
				title = '[font=NanumGothic.ttf]에러 발생[/font]',
				text = '[font=NanumGothic.ttf]Naver 아이디를 입력해 주세요[/font]',
				buttons =[
					MDRaisedButton(
						text='[font=NanumGothic.ttf]확인[/font]', on_release=self.close_dialog
						),
					],
				)
            self.dialog.open()
            return
 
        if self.thread and self.thread.is_alive():
            return

        self.message = Message()
        self.thread = threading.Thread(target=self.run_naverpay_bot, args=(self.message, mode))
        self.thread.start()

        self.event = Clock.schedule_interval(self.update_log_message, 1)
  
    def run_naverpay_bot(self, message, mode):
        bot = NaverPayEventBot()

        user_id = self.root.ids.id.text
        pw = self.root.ids.pw.text

        self.message.text= '로그인을 시도합니다.'
        bot.login(user_id, pw)

        if mode == 'daily':
            self.message.text= '매일 선착순 이벤트를 실행합니다.'
            bot.click_daily_events(self.daily_event_data_tables.row_data, message)
        elif mode == 'onetime':
            self.message.text = '1회성 이벤트를 실행합니다.'
            bot.click_onetime_events(message)

    def update_log_message(self, dt):
        if self.thread.is_alive():
            self.root.ids.log.text = self.message.text
            self.root.ids.progress.value = self.message.progress
        else:
            self.root.ids.log.text = "이벤트 자동 클릭을 완료했습니다."
            self.root.ids.progress.value = 100
            self.event.cancel()
        
    def save_db(self):
        self.db.properties.id = self.root.ids.id.text
        self.db.properties.pw = crypt.encrypt(self.root.ids.pw.text)
        self.db.properties.schedule = self.root.ids.schedule.text

        self.db.save()

    def load_db(self):
        if self.db.load() is False:
            return

        self.root.ids.id.text = self.db.properties.id
        self.root.ids.pw.text = crypt.decrypt(self.db.properties.pw)
        self.root.ids.schedule.text = self.db.properties.schedule

        self.daily_event_data_tables.row_data = []
        for item in self.db.properties.daily_event_list:
            self.daily_event_data_tables.row_data.append(
                (
                    f'[font=NanumGothic.ttf]{item[0]}[/font]',
                    item[1],
                    f'[font=NanumGothic.ttf]{item[2]} 시[/font]'
                )
            )

    def delete_event(self):
        for delete_item in self.delete_candidates:
            # delete from daily_event_data_tables.row_data
            for row_item in self.daily_event_data_tables.row_data:
                if row_item[1] == delete_item:
                    self.daily_event_data_tables.remove_row(row_item)
                    break

            # delete from db.properties.event_list
            for idx in range(len(self.db.properties.daily_event_list)):
                if self.db.properties.daily_event_list[idx][1] == delete_item:
                    del self.db.properties.daily_event_list[idx]
                    break
            
        self.delete_candidates = []
    
    def add_event(self):
        self.db.properties.daily_event_list.append(
            (
                self.root.ids.event_name.text,
                self.root.ids.event_url.text, 
                self.root.ids.event_schedule.text
            )
        )

        self.daily_event_data_tables.add_row(
            (
                f'[font=NanumGothic.ttf]{self.root.ids.event_name.text}[/font]',
                self.root.ids.event_url.text, 
                f'[font=NanumGothic.ttf]{self.root.ids.event_schedule.text}[/font]',
            )
        )

    def on_check_press(self, instance_table, current_row):
        self.delete_candidates.append(current_row[1])    # save URL

    def check_event_time(self, index):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        hour = int(now[0:2])

        # check daily event
        for item in self.db.properties.daily_event_list:
            if hour == int(item[2]):
                self.run_daily_event()

        # check click event
        if hour == int(self.root.ids.schedule.text[0:2]):
            if self.thread and self.thread.is_alive():
                Clock.schedule_once(self.run_click_event, 60)
            else:
                self.run_onetime_event()
            
NaverPayEventPickUp().run()