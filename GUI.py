from PyQt5 import QtWidgets , QtCore , QtGui
from PyQt5.QtWidgets import *
import sys , os
import numpy as np
import pyautogui
import win32api, win32con, win32gui
from win32api import GetSystemMetrics
import cv2
import math
import time
import threading
from numba import jit, cuda
import keyboard
import mouse

class Window(QMainWindow): # GUI Главного меню
    def __init__(self): # Инициализация
        super().__init__()
        ###Инициализация переменных
        self.nameOfTable = None
        ###########################
        self.setWindowTitle('YoloV4App')
        self.resize(600,130)
        self.move(500,500)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName('CentralWidget')
        self.fileCfgWidget()
        self.fileWeightsWidget()
        #self.initEScBox()
        self.trigger = 0


        self.pushButtonStart = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStart.setObjectName('StartButt')
        self.pushButtonStart.setText('Start')
        self.pushButtonStart.move(510, 105)
        self.pushButtonStart.resize(80, 20)

        self.pushButtonStop = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStop.setObjectName('StopButt')
        self.pushButtonStop .setText('Stop')
        self.pushButtonStop .move(410, 105)
        self.pushButtonStop .resize(80, 20)

        self.image_frame = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.labelFDcfg)
        self.layout.addWidget(self.pushButtoncfg)
        self.layout.addWidget(self.line1FDcfg)
        self.layout.addWidget(self.labelFD)
        self.layout.addWidget(self.pushButton)
        self.layout.addWidget(self.line1FD)
        self.layout.addWidget(self.image_frame)

        self.pushButtonStart.clicked.connect(self.yolo_start)
        self.pushButtonStop.clicked.connect(self.yolo_stop)

    def initEScBox(self):
        self.ESLabel = QLabel(self)
        self.ESLabel.setText('Выберите окно:')
        self.ESLabel.move(5, 105)
        self.ESLabel.adjustSize()
        ### CBox
        self.EScBox = QComboBox(self)
        # self.EScBox.addItems(['1','2'])
        self.EScBox.move(100, 105)
        self.EScBox.resize(180, 20)
        self.EScBox.activated[str].connect(self.EScBoxUsing)

    def EScBoxUsing(self, text):
        self.ESnameOfTable = text
        self.loadExcelData(self.path,text)

    def fileCfgWidget(self):
        ####Label
        self.labelFDcfg = QtWidgets.QLabel(self.centralwidget)
        self.labelFDcfg.setText("Укажите путь к файлу .cfg:")
        self.labelFDcfg.move(5,10)
        self.labelFDcfg.adjustSize()
        ####Button:
        self.pushButtoncfg = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtoncfg.setObjectName('FileDialogButton')
        self.pushButtoncfg.setText('Найти')
        self.pushButtoncfg.move(510,30)
        self.pushButtoncfg.resize(80,20)
        ####TextBox:
        self.line1FDcfg = QLineEdit(self.centralwidget)
        self.line1FDcfg.setText(os.path.abspath(os.curdir))
        self.line1FDcfg.resize(500, 20)
        self.line1FDcfg.move(5, 30)
        self.pathcfg = './yolov4-obj.cfg'#os.path.abspath(os.curdir) #Переменная пути
        ####

        self.setCentralWidget(self.centralwidget)
        self.retranslateUicfg()

    def fileWeightsWidget(self):
        ####Label
        self.labelFD = QtWidgets.QLabel(self.centralwidget)
        self.labelFD.setText("Укажите путь к файлу .weight:")
        self.labelFD.move(5,60)
        self.labelFD.adjustSize()
        ####Button:
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName('FileDialogButton')
        self.pushButton.setText('Найти')
        self.pushButton.move(510,80)
        self.pushButton.resize(80,20)
        ####TextBox:
        self.line1FD = QLineEdit(self.centralwidget)
        self.line1FD.setText(os.path.abspath(os.curdir))
        self.line1FD.resize(500, 20)
        self.line1FD.move(5, 80)
        self.path ='./yolov4.weights' #os.path.abspath(os.curdir) #Переменная пути
        ####
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()

    def open_dialog_box(self):
        filename = QFileDialog.getOpenFileName()
        self.path = filename[0]
        self.line1FD.setText(self.path)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate('MainWindow', 'MainWindow'))
        # self.pushButton.setText(_translate('MainWindow', 'button'))
        self.pushButton.clicked.connect(self.open_dialog_box)
    def open_dialog_boxcfg(self):
        filename = QFileDialog.getOpenFileName()
        self.pathcfg = filename[0]
        self.line1FDcfg.setText(self.pathcfg)

    def retranslateUicfg(self):
        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate('MainWindow', 'MainWindow'))
        # self.pushButton.setText(_translate('MainWindow', 'button'))
        self.pushButtoncfg.clicked.connect(self.open_dialog_boxcfg)

    def show_image(self , image):
        self.image = image
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0],
                                  QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def yolo_stop(self):
        self.trigger = 0

    def yolo_start(self):
        self.trigger = 1
        my_thread = threading.Thread(target=self.yolo_start_on())
        my_thread.start()
    @jit(target ="cuda")
    def yolo_start_on(self):
        if self.trigger == 1:
            CONFIG_FILE = self.pathcfg
            WEIGHT_FILE = self.path

            net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHT_FILE)
            # net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

            ln = net.getLayerNames()
            ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            try:
                hwnd = win32gui.FindWindow(None, 'aimlab_tb')
                rect = win32gui.GetWindowRect(hwnd)
                region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

                size_scale = 2
            except:
                region = 0, 0, GetSystemMetrics(0), GetSystemMetrics(1)
                size_scale = 2
            # Get rect of Window
            while self.trigger == 1:
                count = cv2.cuda.getCudaEnabledDeviceCount()
                print(count)
                start = time.time()

                # Get image of screen
                frame = np.array(pyautogui.screenshot(region=region))
                frame_height, frame_width = frame.shape[:2]

                # Detection
                blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)


                net.setInput(blob)
                layerOutputs = net.forward(ln)

                boxes = []
                confidences = []
                start_drawing = time.time()
                for output in layerOutputs:
                    for detection in output:
                        scores = detection[5:]
                        classID = np.argmax(scores)
                        confidence = scores[classID]
                        if confidence > 0.7 and classID == 0:
                            box = detection[:4] * np.array([frame_width, frame_height, frame_width, frame_height])
                            (centerX, centerY, width, height) = box.astype("int")
                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))
                            box = [x, y, int(width), int(height)]
                            boxes.append(box)
                            confidences.append(float(confidence))
                end_drawing = time.time()

                indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.6)

                # Calculate distance for picking the closest enemy from crosshair
                if len(indices) > 0:
                    print(f"Detected:{len(indices)}")
                    min = 99999
                    min_at = 0
                    flags, hcursor, (xx, yy) = win32gui.GetCursorInfo()
                    for i in indices.flatten():
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

                        dist = math.sqrt(math.pow(xx - (x + w / 2), 2) + math.pow(yy - (y + h / 2), 2))
                        if dist < min:
                            min = dist
                            min_at = i

                    # Distance of the closest from crosshair
                    x = int((boxes[min_at][0] + boxes[min_at][2]) / 2 - xx / 1.9)
                    y = int((boxes[min_at][1] + boxes[min_at][3]) / 2 - yy / 1.9)
                    # x = int(boxes[min_at][0] + boxes[min_at][2]/2 - frame_width/2)
                    # y = int(boxes[min_at][1] + boxes[min_at][3]/2 - frame_height/2) - boxes[min_at][3] * 0.5 # For head shot

                    # Move mouse and shoot
                    scale = 1.0
                    x = int(x * scale)
                    y = int(y * scale)
                    # if keyboard.is_pressed('x'):  # if key 'q' is pressed
                    #     print('b is pressed')
                    # win32api.SetCursorPos((x, y))
                    if win32api.GetKeyState(0x02)<0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
                    #time.sleep(0.05)

                end = time.time()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (frame.shape[1] // size_scale, frame.shape[0] // size_scale))
                #self.show_image(frame)
                QApplication.processEvents()
                fps_label = "FPS: %.2f (excluding drawing time of %.2fms)" % (
                1 / (end - start), (end_drawing - start_drawing) * 1000)
                cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                cv2.imshow("frame", frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break


        else:
            pass

def appOn():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    appOn()