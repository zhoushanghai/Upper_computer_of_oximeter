import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from time import sleep
import port_ui
import threading
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class Serial_Qthread_function(QObject):

    signal_start_function = pyqtSignal()
    signal_pushButton_open = pyqtSignal(object)
    signal_pushButton_open_flag = pyqtSignal(object)
    signal_ReadData = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Serial_Qthread_function, self).__init__(parent)
        # 开始调用网络的信号
        print("初始化的时候的线程：", threading.currentThread().ident)
        self.status = 0  # 0表示关闭，1表示打开 2表示occupied/error

    def slot_pushButton_open(self, param):

        if self.status == 0:
            print("prot open", param)
            self.SerialPort.setPortName((param['port']))
            self.SerialPort.setBaudRate(int(param['baud']))
            self.SerialPort.setDataBits(int(param['data']))

            check = 0
            if param['check'] == 'None':
                check = 0
            elif param['check'] == 'Odd':
                check = 3
            else:
                check = 2
            self.SerialPort.setParity(check)
            self.SerialPort.setParity(QSerialPort.NoParity)


            # 判断是否打开串口
            if self.SerialPort.open(QSerialPort.ReadWrite) == False:
                print("打开串口失败")
                self.signal_pushButton_open_flag.emit(0)
                return False
            else:
                print("打开串口成功")
                self.status = 1
                self.signal_pushButton_open_flag.emit(self.status)
                return True
        else:
            print("prot close")
            self.status = 0
            self.SerialPort.close()
            self.signal_pushButton_open_flag.emit(2)

    def SerialReadData_function(self):
        # print("接收数据线程id:", threading.current_thread().ident)
        # print(self.SerialPort.readAll())
        self.signal_ReadData.emit(self.SerialPort.readAll())

    def SerialInit_function1(self):

        print("串口线程id:", threading.current_thread().ident)
        self.SerialPort = QSerialPort()
        self.SerialPort.readyRead.connect(self.SerialReadData_function)
