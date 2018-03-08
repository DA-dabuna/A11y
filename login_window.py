from __future__ import print_function

import os
import psutil
import sys
from multiprocessing import Process

import cv2
import face_recognition
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLineEdit, QLabel, QApplication
from peewee import *

from face_model import FaceUser, create_new_user, find_user
from main_window import open_main_window


class Ui_LoginWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Ui_LoginWindow, self).__init__(parent)

        # self.face_recong = face.Recognition()
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.set_ui()
        self.set_face_data()
        self.set_db()
        self.slot_init()
        self.__flag_work = 0
        self.x = 0
        self.recognized = []
        self.recognized_times = {}

        self.login_success = False

    @staticmethod
    def get_people(folder):
        assert os.path.exists(folder)
        assert os.path.isdir(folder)
        img_list = os.listdir(folder)
        img_list = [item for item in img_list if os.path.isfile(os.path.join(folder, item))]
        return img_list

    def create_user(self):
        flag, color_image = self.cap.read()
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(color_image, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if len(face_locations) == 0:
            print(u"没有识别到人脸")
            ok = QtWidgets.QPushButton()
            message = u"没有识别到人脸，请重新尝试！"
            QtWidgets.QMessageBox.warning(self, u"注册失败", message, buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
            return False
        name = self.name_input.text()
        if not self.name_input_change(name):
            return
        image_name = "".join([name, ".jpeg"])
        target_path = os.path.join(self.BASE_DIR, self.DIR, image_name)
        cv2.imwrite(target_path, color_image,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        if not os.path.exists(target_path):
            print(u"图片创建失败")
            return

        remember_token = create_new_user(name, os.path.join(self.TARGET, image_name))
        if remember_token:
            print(u"用户注册成功")
            temp_image = face_recognition.load_image_file(target_path)
            self.known_face_encodings.append(face_recognition.face_encodings(temp_image)[0])
            self.known_face_names.append(name)
            ok = QtWidgets.QPushButton()
            message = "".join([u"用户[", name, u"]注册成功，", u"您的验证码为", remember_token, u"，确认后点击确定"])
            QtWidgets.QMessageBox.warning(self, u"注册成功", message, buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
            return True

    def set_face_data(self):
        self.BASE_DIR = os.path.dirname(__file__)
        self.DIR = "people"
        self.TARGET = "media"
        self.strict_num = 0.50
        self.target_path = os.path.join(self.BASE_DIR, self.DIR)
        self.known_face_encodings = []
        self.known_face_names = []
        # loading face information
        for item in self.get_people(self.DIR):
            # Load a sample picture and learn how to recognize it.
            temp_image = face_recognition.load_image_file(os.path.join(self.target_path, item))
            self.known_face_encodings.append(face_recognition.face_encodings(temp_image)[0])
            self.known_face_names.append(os.path.splitext(item)[0])
        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.button_open_camera_click()

    def set_db(self):
        BASEDIR = os.path.abspath(os.path.dirname(__file__))
        flag = False
        if not os.path.exists(os.path.join(BASEDIR, 'people.db')) or True:
            flag = True
        self.db = SqliteDatabase('people.db')
        if flag:
            self.db.create_tables([FaceUser])
        self.db.connect()

    def set_ui(self):
        self.name_input = QLineEdit(self)
        self.lb1 = QLabel(self)
        self.lb_name_warning = QLabel(self)
        self.lb_name_warning.move(25, 310)
        self.lb1.move(25, 240)
        self.lb1.setText("[注册]请输入您的姓名")
        self.lb1.adjustSize()
        self.name_input.setMinimumHeight(30)
        self.name_input.move(25, 270)

        # 鼠标状态显示
        pixmap = QPixmap("img/mouse.png")
        self.lb_mouse_status = QLabel(self)
        self.lb_mouse_status.setPixmap(pixmap)
        self.lb_mouse_status.move(25, 350)
        self.lb_mouse_status.resize(100, 120)

        self.name_input.textChanged[str].connect(self.name_input_change)

        self.__layout_main = QtWidgets.QHBoxLayout()
        self.__layout_fun_button = QtWidgets.QVBoxLayout()
        self.__layout_data_show = QtWidgets.QVBoxLayout()

        self.button_register = QtWidgets.QPushButton(u'注册')
        self.button_login = QtWidgets.QPushButton(u'直接登录')
        self.button_register.setMinimumHeight(30)
        self.button_login.setMinimumHeight(30)
        self.button_register.move(10, 220)
        self.button_login.move(10, 350)
        # self.button_open_camera = QtWidgets.QPushButton(u'打开相机')

        self.button_close = QtWidgets.QPushButton(u'退出')
        # self.button_open_camera.setMinimumHeight(30)
        self.button_close.setMinimumHeight(30)

        self.button_close.move(10, 100)

        # 信息显示
        self.label_show_camera = QtWidgets.QLabel()
        self.label_move = QtWidgets.QLabel()
        self.label_move.setFixedSize(200, 200)

        self.label_show_camera.setFixedSize(641, 481)
        self.label_show_camera.setAutoFillBackground(False)

        # self.__layout_fun_button.addWidget(self.button_open_camera)
        self.__layout_fun_button.addWidget(self.button_close)
        self.__layout_fun_button.addWidget(self.button_register)
        self.__layout_fun_button.addWidget(self.button_login)
        self.__layout_fun_button.addWidget(self.label_move)

        self.__layout_main.addLayout(self.__layout_fun_button)
        self.__layout_main.addWidget(self.label_show_camera)

        self.setLayout(self.__layout_main)
        self.label_move.raise_()
        self.setWindowTitle(u'注册 & 登录')
        self.setWindowIcon(QIcon('mouse.png'))

    def showLoginDialog(self):
        opN, okPressed = QtWidgets.QInputDialog.getText(self, u"登录", u"请输入验证码:", QLineEdit.Normal, " ")
        if okPressed and self.token_input_change(opN):
            print(opN)
            users = find_user(opN)
            if len(users) > 0:
                found = False
                for user in users:
                    if user.nickname in self.recognized:
                        if self.recognized_times[user.nickname] >= 4:
                            found = True
                            message = "".join([u"欢迎您，", user.nickname])
                            msg = QtWidgets.QMessageBox.warning(self, u"登陆成功", message,
                                                                buttons=QtWidgets.QMessageBox.Ok,
                                                                defaultButton=QtWidgets.QMessageBox.Ok)
                            p = Process(target=open_main_window, args=())
                            p.start()
                            self.login_success = True
                            self.close()
                            p.join()
                        break
                if not found:
                    print("没有找到用户")
                    QtWidgets.QMessageBox.critical(self, u"错误", u"验证码错误或用户识别错误")
            else:
                print("没有找到验证码的用户")
                QtWidgets.QMessageBox.critical(self, u"错误", u"验证码错误或用户识别错误")
        else:
            print("没有验证码")
            QtWidgets.QMessageBox.critical(self, u"错误", u"验证码错误或用户识别错误")

    def name_input_change(self, text):
        if len(text) <= 0:
            self.lb_name_warning.setText(u"【错误】姓名为空")
            self.lb_name_warning.adjustSize()
            return False
        if len(text) >= 8:
            self.lb_name_warning.setText(u"【错误】姓名过长")
            self.lb_name_warning.adjustSize()
            return False
        return True

    def token_input_change(self, text):
        if len(text) != 4:
            self.lb_token_warning.setText(u"【错误】验证码长度不对")
            self.lb_token_warning.adjustSize()
            return False
        return True

    # def mousePressEvent(self, QMouseEvent):
    #     x = QMouseEvent.x()
    #     y = QMouseEvent.y()
    #     self.label_move.move(0,0)
    #     print(x,y)
    #     print(self.label_move.pos())

    def slot_init(self):
        # self.button_open_camera.clicked.connect(self.button_open_camera_click)
        self.button_login.clicked.connect(self.showLoginDialog)
        self.timer_camera.timeout.connect(self.show_camera)
        self.button_close.clicked.connect(self.close)
        self.button_register.clicked.connect(self.create_user)

    def button_open_camera_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            # if msg==QtGui.QMessageBox.Cancel:
            #                     pass
            else:
                self.timer_camera.start(30)

                # self.button_open_camera.setText(u'关闭相机')
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_camera.clear()
            # self.button_open_camera.setText(u'打开相机')

    def show_camera(self):
        flag, frame = self.cap.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            self.face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                self.face_names.append(name)
                if name not in self.recognized:
                    self.recognized.append(name)
                    self.recognized_times[name] = 1
                else:
                    self.recognized_times[name] = self.recognized_times[name] + 1

        self.process_this_frame = not self.process_this_frame
        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # Display the resulting image
        frame = cv2.resize(frame, (640, 480))
        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(res))

    def closeEvent(self, event):
        if self.login_success:
            self.db.close()
            if self.cap.isOpened():
                self.cap.release()
            if self.timer_camera.isActive():
                self.timer_camera.stop()
            event.accept()
            return

        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()
        self.db.close()
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"关闭", u"是否关闭！")

        msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            if self.cap.isOpened():
                self.cap.release()
            if self.timer_camera.isActive():
                self.timer_camera.stop()
            event.accept()
            p = psutil.Process(os.getpid()).terminate()


def open_login_window():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_LoginWindow()
    ui.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
