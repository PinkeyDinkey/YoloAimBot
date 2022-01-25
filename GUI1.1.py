from PyQt5 import QtWidgets , QtCore , QtGui
from PyQt5.QtWidgets import *
import sys , os
import numpy as np
import win32api, win32con, win32gui
import cv2
import math
import time
import threading


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

        self.trigger = 0
        self.SLabel = QLabel(self)
        self.SLabel.setText('Выберите устройство:')
        self.SLabel.move(5,105)
        self.SLabel.adjustSize()

        self.EScBox = QComboBox(self)
        self.EScBox.addItems(returnCameraIndexes())
        self.EScBox.move(140, 105)
        self.EScBox.resize(180, 20)
        # self.EScBox.activated[str].connect()

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

        self.pushButton.clicked.connect(self.open_dialog_box)
    def open_dialog_boxcfg(self):
        filename = QFileDialog.getOpenFileName()
        self.pathcfg = filename[0]
        self.line1FDcfg.setText(self.pathcfg)

    def retranslateUicfg(self):
        _translate = QtCore.QCoreApplication.translate

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
        self.my_thread = threading.Thread(target=self.yolo_start_on)
        self.my_thread.start()

    def yolo_start_on(self):
        index = int(self.EScBox.currentText())
        if self.trigger == 1:
            CONFIG_FILE = self.pathcfg
            WEIGHT_FILE = self.path

            net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHT_FILE)

            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

            ln = net.getLayerNames()
            ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            print('biba')
            cap = cv2.VideoCapture(index)
            print('boba')
            # Get rect of Window
            while self.trigger == 1:
                print('boba1')
                ret,frame =cap.read()
                size_scale = 2
                print('boba2')

                frame_height, frame_width = frame.shape[:2]

                # Обнаружение
                blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
                net.setInput(blob)
                layerOutputs = net.forward(ln)

                boxes = []
                confidences = []

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

                indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.6)


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

                    # Дистанция к ближайшему объекту
                    x = int((boxes[min_at][0] + boxes[min_at][2]) / 2 - xx / 1.9)
                    y = int((boxes[min_at][1] + boxes[min_at][3]) / 2 - yy / 1.9)


                    # Движение мыши
                    scale = 1.0
                    x = int(x * scale)
                    y = int(y * scale)

                    if win32api.GetKeyState(0x02)<0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)


                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (frame.shape[1] // size_scale, frame.shape[0] // size_scale))
                #self.show_image(frame)
                QApplication.processEvents()
                cv2.imshow("frame", frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

        else:
            pass
def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        try:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(str(index))
                cap.release()
            index += 1
            i -= 1
        except:
            pass
    print(arr)
    return arr

def appOn():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    appOn()

