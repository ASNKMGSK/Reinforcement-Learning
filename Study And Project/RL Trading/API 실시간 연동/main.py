import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import datetime
import random
import pandas as pd


class MyWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        #코스닥 150종목중 50종목 랜덤으로 뽑기
        self.event_code = ['265520', '035760', '058820', '028150', '035900', '035600', '060720', '060250', '030190',
                           '178920', '218410', '036540', '036490', '098460', '215000', '078130', '092730', '007390',
                           '033640', '194700', '144510', '031390', '119860', '032190', '068240', '045390', '078600',
                           '213420', '100130', '086450', '005290', '025900', '060570', '141080', '294140', '058470',
                           '267980', '215200', '235980', '086900', '078160', '140410', '018290', '090460', '082920',
                           '143240', '000250', '038500', '038540', '089980', '006730', '092190', '046890', '178320',
                           '268600', '068760', '091990', '357780', '036830', '192440', '253450', '243840', '108320',
                           '222080', '096530', '025980', '092040', '084850', '067160', '053800', '065660', '131370',
                           '196170', '101490', '056190', '041510', '052020', '237690', '298380', '088800', '028300',
                           '067630', '239610', '230360', '086520', '247540', '183490', '182400', '061970', '290650',
                           '066970', '097520', '039200', '048260', '138080', '122990', '122870', '240810', '104830',
                           '030530', '069080', '044340', '112040', '078070', '023410', '084370', '263050', '272290',
                           '078020', '102710', '039030', '035810', '060150', '048530', '095700', '204270', '036930',
                           '115450', '085660', '278280', '293490', '042000', '078340', '214370', '032500', '290510',
                           '041960', '029960', '033290', '200130', '083790', '214150', '237880', '095610', '200230',
                           '108230', '064760', '034230', '214450', '091700', '263750', '022100', '137400', '003380',
                           '034950', '084990', '048410', '052260', '243070', '145020']
        self.random_list50 = random.sample(self.event_code, 50)  # 코스닥 랜덤 종목 리스트
        self.random_str50 = str(self.random_list50)
        self.random_50=self.random_str50.replace("'", "")
        self.random_50=self.random_50.replace(", ", ";")
        f = open('C:\\Users\\AKS\\Desktop\\list.txt', 'wt')
        f.write(self.random_str50[1:-1])

        self.df_list50 = []#데이터프레임 리스트
        for i in range(50):
            data = {'date':[], 'open':[], 'high':[], 'close':[], 'low':[], 'volume':[]}
            df = pd.DataFrame(data)
            self.df_list50.append(df)
        print(self.df_list50)
        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

        btn = QPushButton("Register", self)
        btn.move(20, 20)
        btn.clicked.connect(self.btn_clicked)

        btn2 = QPushButton("DisConnect", self)
        btn2.move(20, 100)
        btn2.clicked.connect(self.btn2_clicked)

        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._handler_login)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        self.CommmConnect()

    def btn_clicked(self):
        self.SetRealReg("1000", self.random_50, "20;10;13", 1)

    def btn2_clicked(self):
        self.DisConnectRealData("1000")

    def CommmConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")

    def _handler_login(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("login 완료")


    def _handler_real_data(self, code, real_type, data):
        if real_type == "주식체결":
            # 체결 시간
            time = self.GetCommRealData(code, 20)
            second = datetime.datetime.strptime(time, "%H%M%S")
            second_1m = (second-datetime.timedelta(minutes=1)).strftime("%H%M%S")
            '''
            date = datetime.datetime.now().strftime("%Y-%m-%d ")
            date_1m = (datetime.datetime.now()-datetime.timedelta(minutes=1)).strftime("%Y-%m-%d ")
            print(date, date_1m)
            time = datetime.datetime.strptime(date + time, "%Y-%m-%d %H%M%S")
            '''
            # 현재가
            price = self.GetCommRealData(code, 10)
            #print(int(price, end=" "))
            idx = self.random_list50.index(code)
            '''
            # 고가 17
            high = self.GetCommRealData(code, 17)
            #print(int(high, end=" "))
            # 저가 18
            low = self.GetCommRealData(code, 18)
            #print(int(low, end=" "))
            # 시가 16
            open = self.GetCommRealData(code, 16)
            #print(int(open, end=" "))
            '''
            #거래량
            volume = self.GetCommRealData(code, 13)
            print(code, second_1m, abs(int(price)), int(volume))

            '''
            if second_1m[4:] == "00":
                
                self.high = price
                low = price
                open = price
                close = price
            '''
            df0=pd.DataFrame({'date':[second_1m], 'open':[price], 'high':[price], 'close':[price], 'low':[price], 'volume':[volume]})
            self.df_list50[idx]=pd.concat([self.df_list50[idx],df0])
            #self.df_list50[idx].append(df0, ignore_index=True)
            self.df_list50[idx].to_csv("C:\\Users\\AKS\\Desktop\\데이터\\{}.csv".format(code), index=False)



    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                              screen_no, code_list, fid_list, real_type)

    def DisConnectRealData(self, screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)", screen_no)

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
'''
import sys
from pykiwoom.kiwoom import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5.QtCore import *
import datetime
import os
import threading
import random
import pandas as pd
from pandas import Series, DataFrame

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.i=0

        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()


        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 280, 80)

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timer_slot)
        self.list = []#training한 결과를 넣을 리스트
        self.market_start_time = QTime(9, 0, 0)
        self.current_time = QTime.currentTime()
        
        self.event_code = ['265520', '035760', '058820', '028150', '035900', '035600', '060720', '060250', '030190',
                      '178920', '218410', '036540', '036490', '098460', '215000', '078130', '092730', '007390',
                      '033640', '194700', '144510', '031390', '119860', '032190', '068240', '045390', '078600',
                      '213420', '100130', '086450', '005290', '025900', '060570', '141080', '294140', '058470',
                      '267980', '215200', '235980', '086900', '078160', '140410', '018290', '090460', '082920',
                      '143240', '000250', '038500', '038540', '089980', '006730', '092190', '046890', '178320',
                      '268600', '068760', '091990', '357780', '036830', '192440', '253450', '243840', '108320',
                      '222080', '096530', '025980', '092040', '084850', '067160', '053800', '065660', '131370',
                      '196170', '101490', '056190', '041510', '052020', '237690', '298380', '088800', '028300',
                      '067630', '239610', '230360', '086520', '247540', '183490', '182400', '061970', '290650',
                      '066970', '097520', '039200', '048260', '138080', '122990', '122870', '240810', '104830',
                      '030530', '069080', '044340', '112040', '078070', '023410', '084370', '263050', '272290',
                      '078020', '102710', '039030', '035810', '060150', '048530', '095700', '204270', '036930',
                      '115450', '085660', '278280', '293490', '042000', '078340', '214370', '032500', '290510',
                      '041960', '029960', '033290', '200130', '083790', '214150', '237880', '095610', '200230',
                      '108230', '064760', '034230', '214450', '091700', '263750', '022100', '137400', '003380',
                      '034950', '084990', '048410', '052260', '243070', '145020']
        self.random_list50 = random.sample(self.event_code, 50) #코스닥 랜덤 종목 리스트
        self.df_list50 = []
        self.random_str50 = str(self.random_list50)
        print(self.random_list50)
        self.skyrocket_list = [] #급등예측종목리스트

        f = open('C:\\Users\\AKS\\Desktop\\list.txt', 'wt')

        f.write(self.random_str50[1:-1])

        print(self.random_list50)

    def opt10080(self, var_1=1, var_2=1, var_3=0):
        #[opt10080: 주식분봉차트조회요청]
        #데이터 건수를 지정할 수업고, 데이터 유무에따라 한번에 최대 900 개가 조회됩니다.
        #종목코드 = 전문 조회할 종목코드
        #틱범위 = 1:1분, 3: 3분, 5: 5분, 10: 10분, 15: 15분, 30: 30분, 45: 45분, 60: 60분
        #수정주가구분 = 0 or 1, 수신데이터1: 유상증자, 2: 무상증자, 4: 배당락, 8: 액면분할, 16: 액면병합, 32: 기업합병, 64: 감자, 256: 권리락


        result = self.kiwoom.block_request("opt10080", 종목코드=var_1, 틱범위=var_2, 수정주가구분=var_3, output="주식분봉차트조회요청", next=0)
        return result


    def timer_slot(self):

        if self.current_time >= self.market_start_time:
            self.i = self.i + 1
            if self.i < 11:
                print(self.i)
                df = self.opt10080(self, "005930", "1", "0", "주식분봉차트조회")
                df.to_csv('C:\\Documents\\df.csv')
                #df_005930 = DataFrame(df, columns=["종목코드", "현재가", "거래량", "체결시간", "시가", "고가", "저가", "수정주가구분", "수정비율", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"])
                print(df)
                self.text_edit.append(df)
            #if self.i >=11 and len(self.list)!=0:



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec()
'''



'''
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

        #로그임
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        
        self.timer=QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timer_slot)
        
        def timer_slot(self):
            


        btn = QPushButton("Register", self)
        btn.move(20, 20)
        btn.clicked.connect(self.btn_clicked)

        btn2 = QPushButton("DisConnect", self)
        btn2.move(140, 20)
        btn2.clicked.connect(self.btn2_clicked)

        self.text_edit=QTextEdit(self)
        self.text_edit.setGeometry(10, 80, 280, 200)

        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._handler_login)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        self.CommmConnect()

    def btn_clicked(self):
        #self.SetRealReg("1000", "005930", "20;10", 0)
        #self.SetRealReg("2000", "005930", "16;17;10;18;15", 0)
        self.SetRealReg("2000", "005930", "16", 0)
        print("called\n")

    def btn2_clicked(self):
        self.DisConnectRealData("2000")

    def CommmConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")

    def _handler_login(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("login 완료")


    def _handler_real_data(self, code, real_type, data):
        print(code, real_type, data)
        if real_type == "주식시세":
            gubun =  self.GetCommRealData(code, 16)
            remained_time =  self.GetCommRealData(code, 17)
            print(gubun, remained_time)


    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                              screen_no, code_list, fid_list, real_type)

    def DisConnectRealData(self, screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)", screen_no)

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
'''