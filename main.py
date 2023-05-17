import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import time
import numpy as np
import re
import struct
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt5.QtGui import QColor
import portV3
import threading
from serial_thread import Serial_Qthread_function
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import *
import pyqtgraph as s

from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import pic

import pyqtgraph as pg

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5

plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）


# # 创建一个matplotlib图形绘制类
# class MyFigure(FigureCanvas):
#     def __init__(self, width=5, height=4, dpi=100):
#         # 第一步：创建一个创建Figure
#         self.fig = Figure(figsize=(width, height), dpi=dpi)
#         # 第二步：在父类中激活Figure窗口
#         super(MyFigure, self).__init__(self.fig)  # 此句必不可少，否则不能显示图形
#         # 第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
#         self.axes1 = self.fig.add_subplot(311)
#         self.axes2 = self.fig.add_subplot(312)
#         self.axes3 = self.fig.add_subplot(313)

#     # 第四步：就是画图，【可以在此类中画，也可以在其它类中画】

#     def plotsin(self):
#         self.axes0 = self.fig.add_subplot(111)
#         t = np.arange(0.0, 3.0, 0.01)
#         s = np.sin(2 * np.pi * t)
#         self.axes0.plot(t, s)

#     def plotcos(self):
#         t = np.arange(0.0, 3.0, 0.01)
#         s = np.sin(2 * np.pi * t)
#         self.axes.plot(t, s)


# class InitForm(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.ui = port_ui.Ui_Form()
#         self.ui.setupUi(self)
#         self.setWindowTitle("测试")

#     def closeEvent(self, event):
#         print("窗体关闭")


class SerialFrom(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = portV3.Ui_Form()
        self.ui.setupUi(self)
        self.interfaceInit()
        self.uiInit()
        self.setWindowTitle("血氧仪")
        print("主线程ID", threading.currentThread().ident)
        print(threading.active_count())

        self.Serial_Qtread = QThread()
        self.Serial_Qtread_function = Serial_Qthread_function()
        self.Serial_Qtread_function.moveToThread(self.Serial_Qtread)
        self.Serial_Qtread.start()
        self.Serial_Qtread_function.signal_start_function.connect(self.Serial_Qtread_function.SerialInit_function1)
        self.Serial_Qtread_function.signal_start_function.emit()


        self.Serial_Qtread_function.signal_pushButton_open.connect(self.Serial_Qtread_function.slot_pushButton_open)
        self.Serial_Qtread_function.signal_pushButton_open_flag.connect(self.slot_pushButton_open_flag)
        self.Serial_Qtread_function.signal_ReadData.connect(self.slot_ReadData)
        # //-----(‵▽′)/----------------------show  heat wave-----------------------------//
        self.wave_data = []
        self.rate_data = []
        self.spo2_data = []
        self.time_data = []
        self.i = 0
        self.SpO2_Max=0
        self.SpO2_Min=2000
        self.HearRate_Max=0
        self.HearRate_Min=2000

        self.ui.widget_Wave.setPen = pg.mkPen(color='r', width=10)

        self.ui.label_force_tip.setText("欢迎使用")
        self.ui.label_force.setText(" ")





        # hour = [1,2,3,4,5,6,7,8,9,10]
        # temperature = [30,45,34,32,323,31,29,32,35,45]

        # hour 和 temperature 分别是 : x, y 轴上的值
        # self.ui.widget_Wave.plot(hour,temperature,pen=pg.mkPen('b')) # 线条颜色)

        # self.interfaceInit()
        # 波形显示
        # self.dataIndex = 0          # 数据列表当前索引
        # self.dataMaxLength = 10000  # 数据列表最大长度
        # self.dataheader_HeartRate = b'@@:'    # 数据头
        # self.dataheader_Wave = b'$$:'    # 波形数据头
        # self.data_Wave = np.zeros(self.dataMaxLength, dtype=float)
        # self.plotM = pg.PlotWidget()
        # self.plotM.setParent(self.ui.plot_view)
        # self.plotM.setAntialiasing(True)
        # self.canvas_Wave = self.plotM.plot(
        #     self.data_Wave, pen=pg.mkPen(color='r', width=1))

        # self.plot_widget = pg.PlotWidget()
        # # 将 plot_widget 添加到自己定义的 plot_view 上
        # self.plot_widget.setParent(self.plot_view)

        # # 设定 plot_widget 的配置
        # self.plot_widget.setBackground('w')
        # self.plot_widget.setLabel('left', '幅值', color='b', size='14pt')
        # self.plot_widget.setLabel('bottom', '时间', color='b', size='14pt')
        # self.plot_widget.showGrid(x=True, y=True)

        # # 初始化x轴和y轴的数据
        # self.x = [0]
        # self.y = [0]

        # # 心率和血氧
        # self.data_HeartRate = 0
        # self.data_SpO2 = 0

        self.port_Name = []
        self.time_scan = QTimer()
        self.time_scan.timeout.connect(self.Timeout_scan)
        self.time_scan.start(1000)







    def slot_ReadData(self, data):

        Byte_data = bytes(data)
        self.ui.textEdit.insertPlainText(Byte_data.decode('utf-8'))
        if self.ui.checkBox_5.isChecked():
            time_str = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime())+"\r\n"
            self.ui.textEdit.setTextColor(QColor(255, 0, 0))
            self.ui.textEdit.insertPlainText(time_str)
            self.ui.textEdit.setTextColor(QColor(0, 0, 0))
        print(data)
        # data = bytes(data)

        if data.indexOf(b"@") != -1 and data.indexOf(b"#") != -1:
            start_index = data.indexOf(b"@")
            end_index = data.indexOf(b"#")+1
            Wave_data = data[start_index:end_index]
            # Wave_data=bytes(Wave_data)
            print(Wave_data)

            pattern = b'@([\d\.]+)#' # 定义正则表达式匹配模式

            match = re.match(pattern, Wave_data) # 在数据中匹配正则表达式
            if match: # 如果匹配成功
                # value = 65535-int(match.group(1)) # 获取data，并将字符串转换为浮点数
                value = -int(match.group(1)) # 获取data，并将字符串转换为浮点数
                print("value:", value) # 打印提取出来的数据

                # value = -(value-150000)
                #value绝对值
                # if value<0:
                #     value = -value
                # value=value/10
                # value = 65535-value # 获取data，并将字符串转换为浮点数


                # value = float(match.group(1)) # 获取data，并将字符串转换为浮点数

                #只接收最新的100个数据
                if len(self.wave_data) > 100:
                    self.wave_data.pop(0)
                # 将新获取的数据添加到数据列表中

                self.wave_data.append(value)
                # 刷新波形图
                self.update_plot(self.wave_data)

                print("value:", value) # 打印提取出来的数据
            else: # 如果匹配失败
                print("Invalid data format!") # 打印错误提示信息

        if data.indexOf(b"$") != -1 and data.indexOf(b"^") != -1:
            start_index = data.indexOf(b"$")
            end_index = data.indexOf(b"^")+1
            Rate_Spo2 = data[start_index:end_index]
            pattern = b'\$(\d+),(\d+)\^' # 定义正则表达式匹配模式

            match = re.match(pattern, Rate_Spo2) # 在数据中匹配正则表达式
            if match: # 如果匹配成功
                rate = int(match.group(1)) # 获取rate，并将字符串转换为整数
                spo2 = int(match.group(2)) # 获取spo2，并将字符串转换为整数
                 #只接收最新的10个数据
                if len(self.spo2_data) > 6:
                    self.rate_data.pop(0)
                    self.spo2_data.pop(0)
                self.rate_data.append(rate)
                self.spo2_data.append(spo2)


                time_str = time.strftime( "%M:%S", time.localtime())



                self.update_plot_RateSPO2(self.rate_data,self.spo2_data)

                print("rate:", rate, " spo2:", spo2) # 打印提取出来的数据

            else: # 如果匹配失败
                print("Invalid data format!") # 打印错误提示信息

    def show_Force(self,force):
        if force<200:
            self.ui.label_force.setStyleSheet("color: #ef4136;")
            self.ui.label_force_tip.setStyleSheet("color: #ef4136;")
            self.ui.label_force_tip.setText("太重了,放松")
        elif force>200 and force<2000:
            self.ui.label_force.setStyleSheet("color: #7fb80e;")
            self.ui.label_force_tip.setStyleSheet("color: #7fb80e;")
            self.ui.label_force_tip.setText("力度适中")
        elif force>2000:
            self.ui.label_force.setStyleSheet("color: #ef4136;")
            self.ui.label_force_tip.setStyleSheet("color: #ef4136;")
            self.ui.label_force_tip.setText("太轻了")

        self.ui.label_force.setText(str(force))

    def update_plot(self, data_array):

        self.i = self.i + 1
        if self.i > 20:
            self.i = 0
            # arr_new = np.array(data_array[-20:])
            arr_Min = np.min(data_array[-20:])
            arr_Max = np.max(data_array[-20:])
            arr_range = arr_Max - arr_Min
            self.show_Force(arr_range)
            print("arr_Min:", arr_Min, " arr_Max:", arr_Max, " arr_range:", arr_range)
        # data_array=(data_array-arr_Min)/arr_range+0.3

        # data_array=data_array-1
        # 创建画笔对象，并设置线的宽度为2
        pen = pg.mkPen(color='#ed1941', width=3)
        y2 = np.zeros_like(data_array)

        self.ui.widget_Wave.hideAxis('bottom')
        self.ui.widget_Wave.hideAxis('left')
        # line2=self.ui.widget_Wave.plot(y2, pen=pen,clear=True,)
        line=self.ui.widget_Wave.plot(data_array, pen=pen,clear=True,)
        # brush = pg.mkBrush(color=(237, 25, 101, 20))
        # fill = pg.FillBetweenItem(line, x, y1, line2=None, y2=y2, brush=brush)
        # fill = pg.FillBetweenItem(curve1=line, curve2=line2, brush=brush)
        # self.ui.widget_Wave.addItem(fill)

        # self.ui.widget_Wave.plot(data_array[-100:],clear=True,)


    def update_plot_RateSPO2(self, rate_data,spo2_data):

        # barItem = pg.BarGraphItem(x=rate_data,height=y, width = 0.5, brush=(107,200,224))
        barItem = pg.BarGraphItem(x=list(range(len(rate_data))),height=rate_data, width = 0.5, brush=('#d71345'))
        self.ui.widget_Rate.clear()
        self.ui.widget_Rate.addItem(barItem)
        barItem = pg.BarGraphItem(x=list(range(len(spo2_data))),height=spo2_data, width = 0.5, brush=('#b2d235'))
        # barItem = pg.BarGraphItem(height=y, width = 0.5, brush=(107,200,224))
        # barItem = pg.BarGraphItem(x=spo2_data,height=y, width = 0.5, brush=(107,200,224))
        self.ui.widget_SpO2.clear()
        self.ui.widget_SpO2.addItem(barItem)



        # self.ui.widget_Rate.plot( x,y,kind='bar', width=0.5, brush='g')

        # self.ui.widget_Rate.plot( self.time_data,rate_data,kind='bar', width=0.5, brush='g')
        # self.ui.widget_SpO2.plot( self.time_data,spo2_data,kind='bar', width=0.5, brush='g')

        self.ui.label_SpO2.setText(str(spo2_data[-1]))
        self.ui.label_HearRate.setText(str(rate_data[-1]))

        # 判断血氧和心率的最大最小值
        if spo2_data[-1]>self.SpO2_Max:
            self.SpO2_Max=spo2_data[-1]
            self.ui.label_SpO2_Max.setText(str(self.SpO2_Max))
        if spo2_data[-1]<self.SpO2_Min:
            self.SpO2_Min=spo2_data[-1]
            self.ui.label_SpO2_Min.setText(str(self.SpO2_Min))
        if rate_data[-1]>self.HearRate_Max:
            self.HearRate_Max=rate_data[-1]
            self.ui.label_HearRate_Max.setText(str(self.HearRate_Max))
        if rate_data[-1]<self.HearRate_Min:
            self.HearRate_Min=rate_data[-1]
            self.ui.label_HearRate_Min.setText(str(self.HearRate_Min))





    def slot_pushButton_open_flag(self, flag):
        # show serial open flag
        print(flag)
        if flag == 0:
            QMessageBox.warning(self, 'error message', 'occupied 串口打开失败')
        elif flag == 1:
            self.ui.pushButton_open.setStyleSheet("background-color: rgb(255, 0, 255);")
            self.ui.pushButton_open.setText("关闭串口")
            self.ui.pushButton_bt.setStyleSheet("color: white;background-color: rgb(42,92,170)")

            self.ui.pushButton_bt.setText("关闭蓝牙")
            self.time_scan.stop()
        elif flag == 2:
            self.ui.pushButton_open.setStyleSheet("background-color: white;")
            self.ui.pushButton_open.setText("打开串口")
            self.ui.pushButton_bt.setStyleSheet("background-color: white;")
            self.ui.pushButton_bt.setText("打开蓝牙")
            self.time_scan.start(1000)

    def Timeout_scan(self):

        port_list = QSerialPortInfo.availablePorts()
        new_port_list = []
        for port in port_list:
            new_port_list.append(port.portName())

        # print(new_port_list)
        if len(new_port_list) != len(self.port_Name):
            print("扫描串口")
            print(new_port_list)
            self.port_Name = new_port_list
            self.ui.comboBox_com.clear()
            self.ui.comboBox_com.addItems(self.port_Name)

    def interfaceInit(self):
        self.Baud = ('9600', '115200')
        self.Stop = ('1', '1.5', '2')
        self.Data = ('8', '6', '7', '5')
        self.Check = ('None', 'Even', 'Odd', 'Space', 'Mark')

        # self.ui.comboBox_com.addItems(self.port_Name)
        self.ui.comboBox_Baud.addItems(self.Baud)
        self.ui.comboBox_stop.addItems(self.Stop)
        self.ui.comboBox_data.addItems(self.Data)
        self.ui.comboBox_check.addItems(self.Check)

    def uiInit(self):
        self.ui.pushButton_open.clicked.connect(self.pushButton_open_clicked)
        self.ui.pushButton_bt.clicked.connect(self.pushButton_bt_clicked)
        # self.ui.pushButton.clicked.connect(self.pushButton_open_clicked)

        # self.ui.pushButton_close.clicked.connect(self.close_port)
        # self.ui.pushButton_send.clicked.connect(self.send_data)

    def pushButton_open_clicked(self):
        self.set_param = {}
        self.set_param['port'] = self.ui.comboBox_com.currentText()
        self.set_param['baud'] = self.ui.comboBox_Baud.currentText()
        self.set_param['stop'] = self.ui.comboBox_stop.currentText()
        self.set_param['data'] = self.ui.comboBox_data.currentText()
        self.set_param['check'] = self.ui.comboBox_check.currentText()
        self.Serial_Qtread_function.signal_pushButton_open.emit(self.set_param)

    def pushButton_bt_clicked(self):
        self.set_param = {}
        self.set_param['port'] = "COM9"
        self.set_param['baud'] = '115200'
        self.set_param['stop'] = '1'
        self.set_param['data'] = '8'
        self.set_param['check'] = 'None'
        self.Serial_Qtread_function.signal_pushButton_open.emit(self.set_param)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    w1 = SerialFrom()
    w1.show()
    sys.exit(app.exec_())
