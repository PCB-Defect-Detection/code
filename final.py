import datetime
import functools
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QVBoxLayout, QWidget, QGridLayout, QFrame, QHBoxLayout, QMenuBar, QStatusBar
from PyQt5.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt, QThread, pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient, QImage)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QVBoxLayout, QWidget, QGridLayout, QFrame, QHBoxLayout, QMenuBar, QStatusBar
from PyQt5.QtCore import QCoreApplication, QMetaObject, QObject, QPoint, QRect, QSize, QUrl, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QImage
from PyQt5.QtWidgets import QComboBox, QPushButton, QSlider, QTextEdit, QMessageBox, QLineEdit
import subprocess
import serial
import time
import pymysql
import threading
import json
import cv2
import os
import base64
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data.datasets import register_coco_instances
from detectron2 import model_zoo
import numpy as np
import requests
from PIL import Image, ImageOps
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc
import logging



font_path = "C:/Windows/Fonts/malgun.ttf"  # 사용자의 시스템에 맞는 한글 폰트 경로로 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
con = pymysql.connect(host="192.168.31.3",user="root1",password="0000",port=3306,db="pcb",charset='utf8')
cur = con.cursor()

py_serial = serial.Serial(
    port='COM8',
    baudrate=9600,
)
base_dir = "C:\\Users\\jjh99\\PycharmProjects\\pcb"
coco_json = os.path.join(base_dir, "coco_format_1.json")
image_dir = os.path.join(base_dir, "pcb_image")

# COCO JSON 파일에서 카테고리 이름 읽기
with open(coco_json) as f:
    coco_data = json.load(f)
categories = [category['name'] for category in coco_data['categories']]

# 데이터셋 등록
register_coco_instances("my_dataset", {}, coco_json, image_dir)

# Metadata 설정
MetadataCatalog.get("my_dataset").thing_classes = categories

# Config 설정


# ESP32 URL
class ClickableLabel(QLabel):
    clicked = pyqtSignal(object)  # object 타입의 신호로 변경

    def mousePressEvent(self, event):
        self.clicked.emit(self)  # self를 인자로 신호 방출



class ImageWindow(QWidget):
    def __init__(self, pixmap, parent=None):
        super(ImageWindow, self).__init__(parent)
        self.setWindowTitle("확대된 이미지")
        self.setGeometry(300, 100, 1024, 768)
        self.setFixedSize(1024, 768)
        self.label = QLabel(self)
        self.label.setGeometry(QRect(0, 0, 1024, 768))
        self.label.setPixmap(pixmap.scaled(1024, 768, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.show()

    def closeEvent(self, event):
        self.hide()
        if self.parent() is not None:
            self.parent().image_window = None




class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("qt_image/logo.png"))
        self.setWindowTitle("PCB Inspection")
        self.setGeometry(550, 250, 700, 600)
        self.setStyleSheet("background-color: #F0F8FF;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 배경 이미지 추가
        self.background_label = QLabel(self)
        self.background_label.setGeometry(50, 0, 600, 300)
        self.background_label.setPixmap(QPixmap("qt_image/login_logo.png"))
        self.background_label.setScaledContents(True)

        # 텍스트 필드와 버튼을 레이아웃에 추가
        self.input_layout = QVBoxLayout()

        self.idtext = QLineEdit(self)
        self.idtext.setPlaceholderText("ID")
        self.idtext.setFixedHeight(30)
        self.idtext.setFixedWidth(200)
        self.idtext.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ADD8E6;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)
        self.idtext.move(250, 320)

        self.pwtext = QLineEdit(self)
        self.pwtext.setPlaceholderText("PW")
        self.pwtext.setEchoMode(QLineEdit.Password)
        self.pwtext.setFixedHeight(30)
        self.pwtext.setFixedWidth(200)
        self.pwtext.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ADD8E6;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)
        self.pwtext.move(250, 360)

        self.loginBtn = QPushButton("Login", self)
        self.loginBtn.setFixedHeight(30)
        self.loginBtn.setFixedWidth(200)
        self.loginBtn.setStyleSheet("""
            QPushButton {
                border: 2px solid #ADD8E6;
                border-radius: 10px;
                background-color: #F0F8FF;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #B0E0E6;
            }
        """)
        self.loginBtn.clicked.connect(self.btnClick)
        self.loginBtn.move(250, 400)

        self.idtext.returnPressed.connect(self.loginBtn.click)
        self.pwtext.returnPressed.connect(self.loginBtn.click)

        self.layout.addLayout(self.input_layout)
        self.layout.setAlignment(self.input_layout, Qt.AlignCenter)

    def check_login(self, user_id, user_pw):
        try:
            conn = pymysql.connect(host='192.168.31.3', user='root1', password='0000', db='pcb', charset='utf8')
            cur = conn.cursor()
            sql = "SELECT * FROM manager WHERE id = %s AND pw = %s"
            cur.execute(sql, (user_id, user_pw))
            result = cur.fetchone()
            conn.close()
            return result is not None
        except pymysql.Error as e:  # pymysql 예외 처리 추가
            print(f"Error: {e}")
            return False

    def btnClick(self):
        con = pymysql.connect(host="192.168.31.3", user="root1", password="0000", port=3306, db="pcb", charset='utf8')
        cur = con.cursor()
        user_id = self.idtext.text()
        user_pw = self.pwtext.text()

        if self.check_login(user_id, user_pw):

            self.hide()

            self.ui_main_window = QMainWindow()

            self.ui = Ui_MainWindow()

            self.ui.setupUi(self.ui_main_window)

            self.ui_main_window.show()
            QApplication.processEvents()  # 이벤트 루프 갱신

            try:
                time.sleep(1)
                commend = "login"
                py_serial.write(commend.encode())

                time.sleep(2)
                sql = "SELECT * FROM pcb.default_value"
                cur.execute(sql)
                default = cur.fetchall()[0]


                commend = "led " + str(default[1])
                py_serial.write(commend.encode())

                time.sleep(2)
                commend = "motor " + str(default[0])
                py_serial.write(commend.encode())

            except Exception as e:
                print(f"Error: {e}")
        else:
            QMessageBox.warning(self, "로그인 실패", "비밀번호를 다시입력해주세요.")
            self.idtext.clear()
            self.pwtext.clear()



class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.names = []
        self.shapes = []
        self.image_window = None
        self.last_capture_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        self.capture_done = False
        self.current_page = 0
        self.images_per_page = 9
        self.expanded_image = None
        self.is_expanded = False

    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"PCB inspection")
        MainWindow.resize(1600, 900)
        MainWindow.setStyleSheet(u"background-color:rgb(255, 255, 255)")
        MainWindow.setWindowTitle("PCB Inspection")
        MainWindow.setWindowIcon(QIcon("qt_image/logo.png"))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1601, 881))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.left = QFrame(self.gridLayoutWidget)
        self.left.setObjectName(u"left")
        self.left.setFrameShape(QFrame.StyledPanel)
        self.left.setFrameShadow(QFrame.Raised)

        self.main_frame_2 = ClickableLabel(self.left)
        self.main_frame_2.setObjectName(u"main_frame_2")
        self.main_frame_2.setGeometry(QRect(30, 60, 261, 101))
        self.main_frame_2.setPixmap(QPixmap(u"qt_image/sample.png"))
        self.main_frame_2.setScaledContents(True)
        self.main_frame_2.clicked.connect(lambda: self.pages.setCurrentIndex(0))

        self.picture_frame = ClickableLabel(self.left)
        self.picture_frame.setObjectName(u"picture_frame")
        self.picture_frame.setGeometry(QRect(30, 190, 261, 101))
        self.picture_frame.setPixmap(QPixmap(u"qt_image/sample2.png"))
        self.picture_frame.setScaledContents(True)
        self.picture_frame.clicked.connect(lambda: self.pages.setCurrentIndex(1))

        self.percent_frame = ClickableLabel(self.left)
        self.percent_frame.setObjectName(u"percent_frame")
        self.percent_frame.setGeometry(QRect(30, 320, 261, 101))
        self.percent_frame.setPixmap(QPixmap(u"qt_image/sample3.png"))
        self.percent_frame.setScaledContents(True)
        self.percent_frame.clicked.connect(lambda: self.on_percent_frame_click())

        self.setting_frame = ClickableLabel(self.left)
        self.setting_frame.setObjectName(u"setting_frame")
        self.setting_frame.setGeometry(QRect(30, 450, 261, 101))
        self.setting_frame.setPixmap(QPixmap(u"qt_image/sample4.png"))
        self.setting_frame.setScaledContents(True)
        self.setting_frame.clicked.connect(lambda: self.pages.setCurrentIndex(3))


        self.horizontalLayout.addWidget(self.left)

        self.main_frame = QFrame(self.gridLayoutWidget)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QFrame.Raised)

        self.pages = QTabWidget(self.main_frame)
        self.pages.setObjectName(u"pages")
        self.pages.setGeometry(QRect(-10, 0, 1291, 761))
        self.pages.setCurrentIndex(0)
        self.pages.tabBar().hide() # 상단 탭 바 숨기기


        self.main = QWidget()
        self.main.setObjectName(u"main")
        self.cam = QLabel(self.main)
        self.cam.setObjectName(u"cam")
        self.cam.setGeometry(QRect(90, 30, 1024, 600))


        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.75  # Threshold
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # 훈련된 모델 가중치 경로
        cfg.MODEL.DEVICE = "cuda"  # 'cpu' 또는 'cuda'
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(categories)  # 실제 클래스 수로 조정
        predictor = DefaultPredictor(cfg)

        self.thread = video(predictor,"http://192.168.31.176", True)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        self.names=[]

        self.belt_control = QComboBox(self.main)
        self.belt_control.addItem("작동")
        self.belt_control.addItem("정지")
        self.belt_control.addItem("뒤로")
        self.belt_control.addItem("재시작")
        #
        self.belt_control.currentTextChanged.connect(self.motor_control_combo)
        #
        self.belt_control.setObjectName(u"comboBox")
        self.belt_control.setGeometry(QRect(600, 655, 211, 24))
        self.pages.addTab(self.main, "")


        self.picture = QWidget()
        self.picture.setObjectName(u"picture")
        self.gridLayoutWidget_2 = QWidget(self.picture)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(130, 50, 951, 581))
        self.picture_box = QGridLayout(self.gridLayoutWidget_2)
        self.picture_box.setObjectName(u"picture_box")
        self.picture_box.setContentsMargins(0, 0, 0, 0)

        self.frames = []
        for i in range(9):
            frame = ClickableLabel(self.gridLayoutWidget_2)
            frame.setObjectName(f"frame_{i + 1}")
            frame.setFixedSize(256, 192)
            frame.setAlignment(Qt.AlignCenter)
            frame.clicked.connect(lambda _, fr=frame: self.toggle_image_size(fr))  # frame 객체를 인자로 전달

            self.picture_box.addWidget(frame, i // 3, i % 3, 1, 1)
            self.frames.append(frame)

        self.type = QComboBox(self.picture)
        self.type.addItem("전체")
        self.type.addItem("부품 파손")
        self.type.addItem("부품 누락")
        self.type.addItem("스크래치")
        self.type.addItem("정상 커패시터")
        self.type.setObjectName(u"type")
        self.type.setGeometry(QRect(130, 10, 201, 24))
        self.type.currentIndexChanged.connect(self.reset_and_load_images)

        self.previous = QPushButton(self.picture)
        self.previous.setObjectName(u"previous")
        self.previous.setText("<")
        self.previous.setGeometry(QRect(430, 680, 41, 26))
        self.previous.clicked.connect(self.load_previous_images)
        self.next = QPushButton(self.picture)
        self.next.setObjectName(u"next")
        self.next.setText(">")
        self.next.setGeometry(QRect(740, 680, 41, 26))
        self.next.clicked.connect(self.load_next_images)
        self.pages.addTab(self.picture, "")

        self.percent = QWidget()
        self.percent.setObjectName(u"percent")

        self.dailyBtn = QPushButton("일별", self.percent)
        self.dailyBtn.setFixedHeight(25)
        self.dailyBtn.setFixedWidth(50)
        self.dailyBtn.setStyleSheet("""
                                  QPushButton {
                                      border: 2px solid #ADD8E6;
                                      border-radius: 10px;
                                      background-color: #F0F8FF;
                                      padding: 5px;
                                  }
                                  QPushButton:hover {
                                      background-color: #B0E0E6;
                                  }
                                  QPushButton:pressed {
                                      background-color: #B0E0E6;
                                  }
                              """)
        self.dailyBtn.setGeometry(QRect(20, 10, 50, 24))
        self.dailyBtn.clicked.connect(self.show_daily_graph)

        self.monthlyBtn = QPushButton("월별", self.percent)
        self.monthlyBtn.setFixedHeight(25)
        self.monthlyBtn.setFixedWidth(50)
        self.monthlyBtn.setStyleSheet("""
                                  QPushButton {
                                      border: 2px solid #ADD8E6;
                                      border-radius: 10px;
                                      background-color: #F0F8FF;
                                      padding: 5px;
                                  }
                                  QPushButton:hover {
                                      background-color: #B0E0E6;
                                  }
                                  QPushButton:pressed {
                                      background-color: #B0E0E6;
                                  }
                              """)
        self.monthlyBtn.setGeometry(QRect(80, 10, 50, 24))
        self.monthlyBtn.clicked.connect(self.show_monthly_graph)

        self.graph = QLabel(self.percent)
        self.graph.setObjectName(u"label_5")
        self.graph.setGeometry(QRect(90, 70, 971, 561))
        self.pages.addTab(self.percent, "")


        self.setting = QWidget()
        self.setting.setObjectName(u"setting")

        self.pages.currentChanged.connect(self.led_motor_default)

        self.default_setting = QLabel(self.setting)
        self.default_setting.setObjectName(u"led_setting")
        self.default_setting.setText("초기값 설정")
        self.default_setting.setGeometry(QRect(110, 80, 131, 41))

        self.led_setting = QLabel(self.setting)
        self.led_setting.setObjectName(u"LED 값 조정")
        self.led_setting.setText("LED 값 조정")
        self.led_setting.setGeometry(QRect(160, 170, 131, 41))

        self.led_input = QTextEdit(self.setting)
        self.led_input.setObjectName(u"led_input")
        self.led_input.setGeometry(QRect(320, 170, 171, 41))

        self.led_slider = QSlider(self.setting)
        self.led_slider.setObjectName(u"led_slider")
        self.led_slider.setGeometry(QRect(540, 180, 160, 22))
        self.led_slider.setOrientation(Qt.Horizontal)
        self.led_slider.setRange(10,500)
        self.led_slider.setSingleStep(20)
        self.led_slider.sliderReleased.connect(self.led_slider_set)

        self.led_button = QPushButton(self.setting)
        self.led_button.setObjectName(u"led_button")
        self.led_button.setText("설정")
        self.led_button.setGeometry(QRect(750, 180, 160, 22))

        self.led_button.clicked.connect(self.led_def_num)

        self.mot_setting = QLabel(self.setting)
        self.mot_setting.setObjectName(u"mot_setting")
        self.mot_setting.setText("모터 값 조정")
        self.mot_setting.setGeometry(QRect(160, 260, 131, 41))

        self.mot_slider = QSlider(self.setting)
        self.mot_slider.setObjectName(u"mot_slider")
        self.mot_slider.setGeometry(QRect(540, 270, 160, 22))
        self.mot_slider.setOrientation(Qt.Horizontal)
        self.mot_slider.setRange(20,150)
        self.mot_slider.setSingleStep(10)
        self.mot_slider.sliderReleased.connect(self.mot_slider_set)

        self.mot_button = QPushButton(self.setting)
        self.mot_button.setObjectName(u"mot_button")
        self.mot_button.setText("설정")
        self.mot_button.setGeometry(QRect(750, 270, 160, 22))

        self.mot_button.clicked.connect(self.mot_def_num)

        self.mot_input = QTextEdit(self.setting)
        self.mot_input.setObjectName(u"mot_input")
        self.mot_input.setGeometry(QRect(320, 260, 171, 41))
        self.pages.addTab(self.setting, "")

        self.update_btn = QPushButton(self.setting)
        self.update_btn.setObjectName(u"mot_button")
        self.update_btn.setText("업데이트")
        self.update_btn.setGeometry(QRect(450, 570, 160, 22))
        self.update_btn.setStyleSheet("font-size: 25pt;")
        self.update_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update_btn.adjustSize()

        self.update_bar = QProgressBar(self.setting)
        self.update_bar.setObjectName(u"update_bar")
        self.update_bar.setGeometry(QRect(380,500,300,20))
        self.update_bar.setValue(0)
        self.update_btn.clicked.connect(self.run_scripts)
        self.horizontalLayout.addWidget(self.main_frame)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 8)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.frame = QFrame(self.gridLayoutWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color:rgb(240, 248, 255)")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 0, 261, 101))
        self.label.setPixmap(QPixmap(u"qt_image/main_logo.png"))
        self.label.setScaledContents(True)

        self.timer_label = QLabel(self.frame)
        self.timer_label.setObjectName(u"timer_label")
        self.timer_label.setGeometry(QRect(1350,27,120,40))
        self.timer_label.setText("구동시간")
        self.timer_label.setFont(QFont("맑은 고딕",18))

        self.ar_timer = QLabel(self.frame)
        self.ar_timer.setObjectName(u"timer")
        self.ar_timer.setGeometry(QRect(1490,15,200,60))
        self.ar_timer.setFont(QFont("맑은 고딕", 18))

        thread_1 = threading.Thread(target=self.timer)
        thread_1.start()

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.gridLayout.setRowStretch(0, 1)

        self.gridLayout.setRowStretch(1, 8)

        MainWindow.setCentralWidget(self.centralwidget)

        self.load_images()

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def run_scripts(self):
        self.update_bar.setValue(20)
        QApplication.processEvents()  # To update the UI immediately

        def run_in_thread():
            try:
                subprocess.run(['python', 'model.py'], check=True)
                self.update_bar.setValue(40)
                QApplication.processEvents()  # To update the UI immediately

                subprocess.run(['python', 'register_datasets.py'], check=True)
                self.update_bar.setValue(60)
                QApplication.processEvents()  # To update the UI immediately

                subprocess.run(['python', 'train.py'], check=True)
                self.update_bar.setValue(100)
                QMessageBox.information(self, "완료", "모든 스크립트가 성공적으로 실행되었습니다!")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "오류", f"스크립트 실행 중 오류가 발생했습니다: {e}")
                self.update_bar.setValue(0)

        # 백그라운드 스레드에서 실행
        threading.Thread(target=run_in_thread).start()

    def show_daily_graph(self):
        self.show_graph('daily')

    def show_monthly_graph(self):
        self.show_graph('monthly')

    def show_graph(self, period):

        con = pymysql.connect(host="192.168.31.3", user="root1", password="0000", port=3306, db="pcb", charset='utf8')
        cur = con.cursor()

        if period == 'daily':
            query = """
                SELECT DATE(detection_time) as date,
                       SUM(CASE WHEN faulty_type = 'break' THEN 1 ELSE 0 END) as break_count,
                       SUM(CASE WHEN faulty_type = 'omission' THEN 1 ELSE 0 END) as omission_count,
                       SUM(CASE WHEN faulty_type = 'scratch' THEN 1 ELSE 0 END) as scratch_count,
                       SUM(CASE WHEN faulty_type = 'normal_cap' THEN 1 ELSE 0 END) as normal_cap_count
                FROM faulty
                GROUP BY DATE(detection_time)
                ORDER BY date
            """
        else:  # monthly
            query = """
                SELECT DATE_FORMAT(detection_time, '%Y-%m') as month,
                       SUM(CASE WHEN faulty_type = 'break' THEN 1 ELSE 0 END) as break_count,
                       SUM(CASE WHEN faulty_type = 'omission' THEN 1 ELSE 0 END) as omission_count,
                       SUM(CASE WHEN faulty_type = 'scratch' THEN 1 ELSE 0 END) as scratch_count,
                       SUM(CASE WHEN faulty_type = 'normal_cap' THEN 1 ELSE 0 END) as normal_cap_count
                FROM faulty
                GROUP BY month
                ORDER BY month
            """

        cur.execute(query)
        rows = cur.fetchall()
        con.close()

        dates = [row[0].strftime('%Y년 %m월 %d일') if period == 'daily' else row[0] + "월" for row in rows]
        break_counts = [row[1] for row in rows]
        omission_counts = [row[2] for row in rows]
        scratch_counts = [row[3] for row in rows]
        normal_cap_counts = [row[4] for row in rows]

        fig, ax = plt.subplots()
        width = 0.2  # Width of the bars
        x = range(len(dates))

        ax.bar([p - 1.5 * width for p in x], break_counts, width=width, label='Break', color='skyblue')
        ax.bar([p - 0.5 * width for p in x], omission_counts, width=width, label='Omission', color='lightgreen')
        ax.bar([p + 0.5 * width for p in x], scratch_counts, width=width, label='Scratch', color='salmon')
        ax.bar([p + 1.5 * width for p in x], normal_cap_counts, width=width, label='Normal Cap', color='orange')

        if period == 'daily':
            ax.set_title('일별 결함 유형')
            ax.set_xlabel('날짜')
        else:
            ax.set_title('월별 결함 유형')
            ax.set_xlabel('월')

        ax.set_ylabel('결함 수')
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=0, ha='center')
        ax.legend()

        canvas = FigureCanvas(fig)
        canvas.draw()

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)

        image = Image.open(buf)
        qim = QPixmap.fromImage(QImage(image.tobytes(), image.width, image.height, QImage.Format_RGBA8888))
        qim = qim.scaled(self.graph.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.graph.setPixmap(qim)
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.main_frame_2.setText("")
        self.picture_frame.setText("")
        self.percent_frame.setText("")
        self.setting_frame.setText("")
        self.pages.setTabText(self.pages.indexOf(self.main), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.pages.setTabText(self.pages.indexOf(self.picture), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.pages.setTabText(self.pages.indexOf(self.percent), QCoreApplication.translate("MainWindow", u"\ucabd", None))
        self.pages.setTabText(self.pages.indexOf(self.setting), QCoreApplication.translate("MainWindow", u"\ucabd", None))
        self.label.setText("")

    # 정지, 작동, 뒤로
    def motor_control_combo(self):
        if (self.belt_control.currentText() == "작동"):
            commend = "run"
            py_serial.write(commend.encode())
        elif (self.belt_control.currentText() == "정지"):
            commend = "stop"
            py_serial.write(commend.encode())
        elif (self.belt_control.currentText() == "뒤로"):
            commend = "back"
            py_serial.write(commend.encode())
        elif (self.belt_control.currentText() == "재시작"):
            commend = "restart"
            py_serial.write(commend.encode())
    # led, motor 기본값 적용
    def led_motor_default(self,index):
        if self.pages.widget(index) == self.setting:
            try:
                sql = "SELECT * FROM pcb.default_value"
                cur.execute(sql)
                default = cur.fetchall()[0]
                self.mot_input.clear()
                self.mot_input.append(str(default[0]))
                self.mot_slider.setValue(default[0])

                time.sleep(0.1)
                self.led_input.clear()
                self.led_input.append(str(default[1]))
                self.led_slider.setValue(default[1])
            except Exception as e:
                print(e)
    # 구동시간
    def timer(self):
        try:
            while True:
                response = py_serial.readline()
                print(response.decode())
                # 구동시간
                if response.decode().startswith("timer"):
                    value = int(response[:len(response) - 1].decode().split(" ")[1])
                    if value >= 60:
                        min = value // 60
                        sec = value % 60
                    else:
                        min = 0
                        sec = value
                    if min >= 10 and sec >= 10:
                        self.ar_timer.setText(f"{min} : {sec}")
                    elif min >= 10 and sec < 10:
                        self.ar_timer.setText(f"{min} : 0{sec}")
                    elif min < 10 and sec >= 10:
                        self.ar_timer.setText(f"0{min} : {sec}")
                    elif min < 10 and sec < 10:
                        self.ar_timer.setText(f"0{min} : 0{sec}")
                elif "capture" in response.decode():
                    current_time = datetime.datetime.now()
                    if not self.capture_done and (current_time - self.last_capture_time > datetime.timedelta(
                            seconds=10)):  # 캡처가 완료되지 않았고 마지막 캡처 후 10초가 지난 경우
                        self.last_capture_time = current_time

                        py_serial.write("stop".encode())
                        time.sleep(3)  # 캡처하기 전에 3초 지연
                        self.capture_image(self.names, self.thread.shapes)
                        py_serial.write("restart".encode())
                        self.capture_done = True
                elif "reset_belt" in response.decode():
                    print("들어옴")

                    self.capture_done = False  # Reset capture flag if necessary

        except Exception as e:
            print(e)

    # led 값 조절
    def led_def_num(self):
        text = self.led_input.toPlainText()
        try:
            if (text != " " and text.isdigit() and 10 <= int(text) <= 500 ):
                self.led_slider.setValue(int(text))
                commend = "led " + text
                py_serial.write(commend.encode())
                sql = "SELECT led FROM pcb.default_value"
                if (cur.execute(sql) == 0):
                    sql = f"INSERT INTO pcb.default_value (led) VALUES ({text});"
                    cur.execute(sql)
                    con.commit()
                else:
                    sql = f"UPDATE default_value SET led = '{text}';"
                    cur.execute(sql)
                    con.commit()
            elif (int(text) < 100 or int(text) > 600):
                QMessageBox.about(self.mot_slider, 'Error', '잘못된 값입니다.')
            else:
                print("제대로 입력해주세요")
        except Exception as e:
            print(e)
    # motor 값 조절
    def mot_def_num(self):
        text = self.mot_input.toPlainText()
        try:
            if (text != " " and text.isdigit() and 20 <= int(text) <= 150):
                self.mot_slider.setValue(int(text))
                commend = "motor " + text
                py_serial.write(commend.encode())
                sql = "SELECT motor FROM pcb.default_value"
                if (cur.execute(sql) == 0):
                    sql = f"INSERT INTO pcb.default_value (motor) VALUES ({text});"
                    cur.execute(sql)
                    con.commit()
                else:
                    sql = f"UPDATE default_value SET motor = '{text}';"
                    cur.execute(sql)
                    con.commit()
            elif (int(text) < 20 or int(text) > 150):
                QMessageBox.about(self.mot_slider, 'Error', '잘못된 값입니다.')
            else:
                print("제대로 입력해주세요")
        except Exception as e:
            print(e)
    def led_slider_set(self):
        try:
            commend = "led " + str(self.led_slider.value())
            py_serial.write(commend.encode())
            self.led_input.clear()
            self.led_input.append(str(self.led_slider.value()))
            sql = "SELECT led FROM pcb.default_value"
            if (cur.execute(sql) == 0):
                sql = f"INSERT INTO pcb.default_value (led) VALUES ({self.led_slider.value()});"
                cur.execute(sql)
                con.commit()
            else:
                sql = f"UPDATE default_value SET led = '{self.led_slider.value()}';"
                cur.execute(sql)
                con.commit()
            time.sleep(1)
        except Exception as e:
            print(e)
    def mot_slider_set(self):
        try:
            commend = "motor " + str(self.mot_slider.value())
            py_serial.write(commend.encode())
            self.mot_input.clear()
            self.mot_input.append(str(self.mot_slider.value()))
            sql = "SELECT motor FROM pcb.default_value"
            if (cur.execute(sql) == 0):
                sql = f"INSERT INTO pcb.default_value (motor) VALUES ({self.mot_slider.value()});"
                cur.execute(sql)
                con.commit()
            else:
                sql = f"UPDATE default_value SET motor = '{self.mot_slider.value()}';"
                cur.execute(sql)
                con.commit()
            time.sleep(1)
        except Exception as e:
            print(e)

    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        self.current_qt_img = cv_img  # 현재 이미지를 저장
        qt_img = QPixmap.fromImage(cv_img)
        self.cam.setPixmap(qt_img)

    def capture_image(self, names, shapes):
        folder = "save_pcb"
        prefix = "captured_image_"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = self.get_next_filename(folder, prefix)
        img_path = filename.replace(".json", ".jpg")

        if hasattr(self.thread, 'original_frame') and self.thread.original_frame is not None:
            original_frame = self.thread.original_frame

            # BGR에서 RGB로 변환
            rgb_image = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)

            resized_image = cv2.resize(rgb_image, (1024, 768))
            cv2.imwrite(img_path, resized_image)

            print(f"Image saved as {img_path}")

            self.save_to_database(img_path, names)
            self.create_and_save_json(img_path, shapes)

    def get_next_filename(self, folder, prefix):
        files = os.listdir(folder)
        max_number = 0
        for file in files:
            if file.startswith(prefix) and file.endswith('.jpg'):
                try:
                    number = int(file[len(prefix):-4])
                    if number > max_number:
                        max_number = number
                except ValueError:
                    continue
        next_number = max_number + 1
        return os.path.join(folder, f"{prefix}{next_number}.jpg")

    def save_to_database(self, filename, names):

        names = self.thread.names

        print(names)
        with open(filename, 'rb') as f:
            img_data = f.read()
        try:
            with con.cursor() as cursor:
                names=self.thread.names

                for name in names:
                    # Check if the same faulty_type was stored in the last 10 seconds
                    sql_check = """
                                       SELECT COUNT(*) FROM faulty 
                                       WHERE faulty_type = %s 
                                         AND detection_time >= NOW() - INTERVAL 10 SECOND
                                       """
                    cursor.execute(sql_check, (name,))
                    result = cursor.fetchone()

                    if result[0] == 0:
                        # Insert if no record found in the last 10 seconds
                        sql_insert = "INSERT INTO faulty (image, faulty_type, detection_time) VALUES (%s, %s, NOW())"
                        cursor.execute(sql_insert, (img_data, name))

                    else:
                        logging.debug(f"Record with faulty_type '{name}' not inserted due to recent duplicate.")

            con.commit()
        finally:
            pass

    def create_and_save_json(self,img_path, shapes):


        if not shapes:  # shapes 리스트가 비어있는지 확인

            return

        base64_image_data, image_height, image_width = encode_image_to_base64(img_path)
        json_data = create_json(img_path, base64_image_data, image_height, image_width, shapes)
        json_path = img_path.replace(".jpg", ".json")
        save_json(json_data, json_path)


    def reset_and_load_images(self):
        self.current_page = 0
        self.load_images()

    def load_images(self):
        con = pymysql.connect(host="192.168.31.3", user="root1", password="0000", port=3306, db="pcb", charset='utf8')
        cur = con.cursor()
        selected_type = self.type.currentText()
        query = "SELECT image FROM faulty"
        if selected_type == "부품 파손":
            query += " WHERE faulty_type = 'break'"
        elif selected_type == "부품 누락":
            query += " WHERE faulty_type = 'omission'"
        elif selected_type == "스크래치":
            query += " WHERE faulty_type = 'scratch'"
        elif selected_type == "정상 커패시터":
            query += " WHERE faulty_type = 'normal_cap'"
        offset = self.current_page * self.images_per_page
        query += f" ORDER BY detection_time DESC LIMIT {self.images_per_page} OFFSET {offset}"
        cur.execute(query)
        rows = cur.fetchall()
        con.close()

        for i, frame in enumerate(self.frames):
            if i < len(rows):
                try:
                    image_data = rows[i][0]
                    image = Image.open(io.BytesIO(image_data))
                    image = image.convert("RGBA")
                    data = image.tobytes("raw", "RGBA")
                    qim = QPixmap.fromImage(QImage(data, image.width, image.height, QImage.Format_RGBA8888))
                    qim = qim.scaled(256, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    frame.setPixmap(qim)

                except Exception as e:

                    frame.clear()
            else:
                frame.clear()

        self.next.setEnabled(len(rows) == self.images_per_page)
        self.previous.setEnabled(self.current_page > 0)


    def on_percent_frame_click(self):

        self.pages.setCurrentIndex(2)
        self.show_daily_graph()
    def load_previous_images(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_images()

    def load_next_images(self):
        self.current_page += 1
        self.load_images()

    def toggle_image_size(self, sender):
        if sender is None:
            logging.error("Sender is None")
            return

        try:
            pixmap = sender.pixmap()
            if pixmap is None:

                return

            if self.image_window is not None:
                self.image_window.hide()
                self.image_window = None

            self.image_window = ImageWindow(pixmap)  # 부모를 설정하지 않음

        except Exception as e:
            logging.error(f"Error in toggle_image_size: {e}")

    def closeEvent(self, event):
        if self.image_window is not None:
            self.image_window.close()  # 메인 윈도우 닫힐 때 서브 윈도우도 닫기
        event.accept()

class video(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    def __init__(self, predictor, url, awb):
        super().__init__()
        self.predictor = predictor
        self.url = url
        self.AWB = awb
        self.running = True
        self.current_frame = None
        self.names=[]
        self.shapes = []
        self.original_frame = None
    def set_resolution(self,url: str, index: int = 1, verbose: bool = False):
        try:
            if verbose:
                resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
                print("available resolutions\n{}".format(resolutions))

            if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
                requests.get(url + "/control?var=framesize&val={}".format(index))
            else:
                print("Wrong index")
        except:
            print("SET_RESOLUTION: something went wrong")

    def run(self):
        self.set_resolution(self.url, index=8)
        cap = cv2.VideoCapture(self.url + ":81/stream")
        while self.running:
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    try:
                        input_height, input_width = frame.shape[:2]
                        outputs = self.predictor(frame)
                        v = Visualizer(frame[:, :, ::-1],
                                       metadata=MetadataCatalog.get("my_dataset"),
                                       scale=0.8,
                                       instance_mode=ColorMode.IMAGE
                                       )
                        v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
                        rgb_image = v.get_image()[:, :, ::-1]
                        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
                        self.original_frame = bgr_image.copy()
                        h, w, ch = bgr_image.shape
                        bytes_per_line = ch * w
                        convert_to_Qt_format = QImage(bgr_image.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
                        p = convert_to_Qt_format.scaled(1024, 768, Qt.KeepAspectRatio)
                        self.change_pixmap_signal.emit(p)

                        classes = outputs["instances"].pred_classes
                        boxes = outputs["instances"].pred_boxes.tensor.cpu().numpy()
                        a = []
                        shapes = []
                        for cls, box in zip(classes, boxes):
                            class_name = MetadataCatalog.get("my_dataset").thing_classes[cls]
                            a.append(str(class_name))
                            x1, y1, x2, y2 = box
                            scale_x = 1024 / input_width
                            scale_y = 768 / input_height
                            x1 *= scale_x
                            y1 *= scale_y
                            x2 *= scale_x
                            y2 *= scale_y
                            shape = {
                                "label": class_name,
                                "points": [
                                    [x1, y1],
                                    [x2, y1],
                                    [x2, y2],
                                    [x1, y2]
                                ],
                                "group_id": None,
                                "description": "",
                                "shape_type": "polygon",
                                "flags": {},
                                "mask": None
                            }
                            shapes.append(shape)
                        self.names = a
                        self.shapes = shapes
                    except Exception as e:
                        print(f"Error: {e}")
        cap.release()

    def stop(self):
        self.running = False
        self.wait()

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            return encoded_string, img.height, img.width
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None, None, None

def create_json(image_path, base64_image_data, image_height, image_width, shapes):
    if not base64_image_data:
        return None

    for shape in shapes:
        shape['points'] = [[float(x), float(y)] for x, y in shape['points']]
        shape['shape_type'] = "polygon"

    json_data = {
        "version": "5.4.1",
        "flags": {},
        "shapes": shapes,
        "imagePath": os.path.basename(image_path),
        "imageData": base64_image_data,
        "imageHeight": image_height,
        "imageWidth": image_width
    }
    return json_data



def save_json(json_data, json_path):
    if not json_data:

        return

    try:
        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    except Exception as e:
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a=MyWindow()
    a.show()
    sys.exit(app.exec_())
    commend = "end"
    py_serial.write(commend.encode())
