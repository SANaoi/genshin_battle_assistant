import time
import random
from ctypes import windll
import difflib
 

from PyQt5.QtWidgets import (QLabel, QMainWindow, QVBoxLayout, 
                             QWidget, QPushButton, QGraphicsDropShadowEffect)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QFontDatabase, QFont

from source.capture import capture
from source.ocr_module import ocr
from source.rec import *
from source.util import SecondWindow

init_role = ["绫华","心海","万叶","申鹤"]
test_role_info = [{"now_role": "绫华", 
                   "skill_key": "q", 
                   "skill_cd": 9.8},
                  {"now_role": "心海", 
                   "skill_key": "e", 
                   "skill_cd": 9.8},
                  {"now_role": "绫华", 
                   "skill_key": "e", 
                   "skill_cd": 9.8}]
test_info = random.choice(test_role_info)



class CountdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("没想好")
        self.setGeometry(1300, 200, 300, 400)

        self.setAttribute(Qt.WA_TranslucentBackground)
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)   
        self.layout = QVBoxLayout(self.central_widget)

        font_id = QFontDatabase.addApplicationFont("fonts\舟方日明体斜体.otf")
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(self.font_family)
        font.setBold(1000-7)
        font.setPointSize(16)
        self.font = font
        self.setFont(self.font)

        self.role_timers = {}  
        self.role_labels = {} 
        self.skill_timestamps = {} 

        self.team_roles = 0
        self.is_rename_team = 0
        self.ocr = 0

        # 鼠标按下时的初始位置
        self.drag_position = QPoint()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui_info)

        self.init_button = QPushButton('CD检测器,启动！')
        self.layout.addWidget(self.init_button)
        self.init_button.clicked.connect(self.init_base)
        
        self.close_button = QPushButton('关闭', self)
        self.layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)
        
    def init_base(self): # 初始化  
        self.handle = windll.user32.FindWindowW(None, "原神")
        if not self.handle:
            return SecondWindow(info="未启动原神或未窗口化").exec_()
        
        if not self.is_rename_team:
            self.ocr = ocr()
            
            self.is_rename_team = 1
        else:
            self.re_init_base()
        self.image = capture(self.handle)

        if type(self.image) == bool:
            return SecondWindow(info="请勿最小化").exec_()
        
        self.team_roles = rec_team_roles(self.image, self.ocr)

        if not self.team_roles:
            return SecondWindow(info="未找到任何角色").exec_()
            
        self.init_label(self.team_roles)
        self.init_timer()
        self.event_loop()

    def init_label(self, team_role):
        skill_key = ["E"]
        if len(team_role) >= 4:
            team_role = team_role[:4]
        for key in skill_key:
            for role_name in team_role: 
                label_id = f"{role_name}_{key}"
                label = QLabel(self)

                self.role_labels[label_id] = label
                self.layout.addWidget(label)

    def init_timer(self):
        for label_id, _ in self.role_labels.items():
            timer = QTimer(self)
            timer.setInterval(128)
            self.role_timers[label_id] = {"timer": timer, "skill_cd": -1}

            skill_cd = self.role_timers[label_id]["skill_cd"]
            label = self.role_labels[label_id]
            label.setText(f"{label_id}: {skill_cd}")
            # 设置文本颜色
            self.set_text_shadow(label)

            label.setStyleSheet(f"""
                                color: rgb(255,255,255); 
                                margin:10; 
                                background-color: rgba(0,0,0,0.2);
                                border-width: 2px;
                                border-radius: 10px;
                                font-family: {self.font_family };
                                font: bold 18px;
                                min-width: 10em;
                                min-height: 2em;
                                padding: 6px;""")


    def re_init_base(self):
        for label_id, label in self.role_labels.items():
            self.layout.removeWidget(label)
            label.deleteLater()

            timer_info = self.role_timers[label_id]
            timer = timer_info["timer"]
            timer.stop()
            timer.deleteLater()
        self.role_labels = {}
        self.role_timers = {}
    
    def update_skill_cd(self, rec_content):
        if rec_content["skill_E"]:
            now_role, skill_E = rec_content["now_role"], rec_content["skill_E"]
            now_role = f"{now_role}_{skill_E}"    
            for label_id, timer_info in self.role_timers.items():
                if now_role == label_id:
                    skill_cd = timer_info["skill_cd"]
                    current_timestamp = int(time.time() * 1000)
                    end_time = current_timestamp + rec_content["skill_cd_E"]*1000
                    self.skill_timestamps[label_id] = end_time

                    if skill_cd == -1:
                        timer_info["skill_cd"] = rec_content["skill_cd_E"]*1000
                        timer_info["timer"].timeout.connect(lambda t=label_id: self._update_cd(t))
                        timer_info["timer"].start()
                    elif skill_cd <= 0:
                        timer_info["skill_cd"] = rec_content["skill_cd_E"]*1000
                        timer_info["timer"].start()

        # if rec_content["skill_Q"]:
        #     now_role, skill_Q = rec_content["now_role"], rec_content["skill_Q"]
        #     now_role = f"{now_role}_{skill_Q}"    
        #     for label_id, timer_info in self.role_timers.items():
        #         if now_role == label_id:
        #             skill_cd = timer_info["skill_cd"]
    
        #             current_timestamp = int(time.time() * 1000)
        #             end_time = current_timestamp + rec_content["skill_cd_Q"]*1000
        #             self.skill_timestamps[label_id] = end_time
            
        #             if skill_cd == -1:
        #                 timer_info["skill_cd"] = rec_content["skill_cd_Q"]*1000
        #                 timer_info["timer"].timeout.connect(lambda t=label_id: self._update_cd(t))
        #                 timer_info["timer"].start()
        #             elif skill_cd <= 0:
        #                 timer_info["skill_cd"] = rec_content["skill_cd_Q"]*1000
        #                 timer_info["timer"].start()
        
    
    def _update_cd(self, label_id):
        timer_info = self.role_timers[label_id]
        # skill_cd = timer_info["skill_cd"]
        current_time = int(time.time() * 1000)
        label = self.role_labels[label_id]
        skill_cd = self.skill_timestamps[label_id] - current_time
        if skill_cd > 0:
            self.set_text_shadow(label)
            label.setStyleSheet(f"""
                                color: rgb(255,255,255); 
                                margin:10; 
                                border-width: 2px;
                                border-radius: 10px;
                                font-family: {self.font_family };
                                font: bold 18px;
                                min-width: 10em;
                                min-height: 2em;
                                padding: 6px;""")
            skill_cd -= 128
            timer_info["skill_cd"] = skill_cd

            self._update_display(label_id)
        else:
            timer_info["skill_cd"] = 0
            self._update_display(label_id)
            self.set_text_shadow(label)
            label.setStyleSheet(f"""
                                color: rgb(255,255,255); 
                                margin:10; 
                                background-color: rgba(0,0,0,0.2);
                                border-width: 2px;
                                border-radius: 10px;
                                font-family: {self.font_family };
                                font: bold 18px;
                                min-width: 10em;
                                min-height: 2em;
                                padding: 6px;""")
            timer_info["timer"].stop()
    
    def _update_display(self, label_id):
        timer_info = self.role_timers[label_id]
        remaining_time = timer_info["skill_cd"]
        seconds = remaining_time // 1000
        milliseconds = remaining_time % 1000
        label = self.role_labels[label_id]
        label.setText(f"{label_id}: {seconds:02.0f}.{milliseconds:03.0f}")
        

    def event_loop(self):
        self.update_timer.start(256)    

    def update_ui_info(self):
        if self.ocr:
            rec_content = rec_key(self.handle, self.ocr)
        else:
            self.update_timer.stop()
            return SecondWindow(info="未初始化").exec_()
        
        # self.is_update_now_team_roles()

        if rec_content:
            self.update_skill_cd(rec_content)

    def mousePressEvent(self, event):
        #鼠标左键按下
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
      
            
    def mouseMoveEvent(self, event):
        #鼠标左键按下的同时移动鼠标
        if event.buttons() and Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def enterEvent(self, event):
        self.init_button.setVisible(True)
        self.close_button.setVisible(True)
    def leaveEvent(self, event):
        if self.team_roles:
            self.init_button.setVisible(False)
            self.close_button.setVisible(False)

    def set_text_shadow(self, label):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(2)
        shadow.setOffset(0)
        shadow.setColor(Qt.red)
  
        label.setGraphicsEffect(shadow)
    
    def paintEvent(self, event):
        # 在paintEvent中绘制窗口背景
        painter = QPainter(self)
        # 使用QColor来设置颜色的透明度
        background_color = QColor(0, 0, 0, 1)  #
        painter.fillRect(self.rect(), background_color)
    
    def is_update_now_team_roles(self):
        image = capture(self.handle)
        now_roles = rec_team_roles(image, self.ocr)

        if now_roles and self.team_roles:
            a = "".join(self.team_roles)
            b = "".join(now_roles)
            count =  difflib.SequenceMatcher(None, a, b).quick_ratio()
            if count < 0.5:
                self.image = capture(self.handle)
                self.team_roles = now_roles
                self.re_init_base()
                self.init_label(self.team_roles)
                self.init_timer()



        

    