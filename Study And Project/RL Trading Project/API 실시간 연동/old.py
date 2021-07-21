import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
'''
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyStock")
        self.setGeometry(300, 300, 300, 150)

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 280, 80)
        self.text_edit.setEnabled(False)

        self.kiwoom.OnEventConnect.connect(self.event_connect)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")
'''
if __name__ == "__main__":

    '''
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

    
        btn1 = QPushButton("Login", self)
        btn1.move(20, 20)
        btn1.clicked.connect(self.btn1_clicked)

        btn2 = QPushButton("Check state", self)
        btn2.move(20, 70)
        btn2.clicked.connect(self.btn2_clicked)

    def btn1_clicked(self):
        ret = self.kiwoom.dynamicCall("CommConnect()")
        print("ret:", ret)
        #ret = self.kiwoom.dynamicCall("CommConnect()")

    def btn2_clicked(self):
        if self.kiwoom.dynamicCall("GetConnectState()") == 0:
            self.statusBar().showMessage("Not connected")
        else:
            self.statusBar().showMessage("Connected")
    '''
'''
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QAxContainer import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Kiwoom Login
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        # OpenAPI+ Event
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata) #OnReceiveTrData 이벤트가 발생하여 서버에서 데이터를 받아서 commgetdata 호출해서 데이터를 가져온다.

        self.setWindowTitle("PyStock")
        self.setGeometry(300, 300, 300, 150)

        label = QLabel('종목코드: ', self)
        label.move(20, 20)

        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 20)
        self.code_edit.setText("039490")

        btn1 = QPushButton("조회", self)
        btn1.move(190, 20)
        btn1.clicked.connect(self.btn1_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 280, 80)
        self.text_edit.setEnabled(False)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")

    def btn1_clicked(self):
        code = self.code_edit.text()
        self.text_edit.append("종목코드: " + code)

        # SetInputValue  SetInputValue 메서드를 사용해 TR 입력 값을 설정합니다.
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

        # CommRqData  CommRqData 메서드를 사용해 TR을 서버로 송신합니다.
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")
        # 첫번째 인자는 tr구분을 위한것, 두번째 인자는 요청하는 tr이름입력, 세번째 인자는 단순조회tr이어서 0입력, 4번째는 화면번호

    # CommGetData 메서드를 사용해 수신 데이터를 가져옵니다.
    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "거래량")

            self.text_edit.append("종목명: " + name.strip()) #문자열의 공백제거
            self.text_edit.append("거래량: " + volume.strip())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
'''
'''
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QAxContainer import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Kiwoom Login
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        # OpenAPI+ Event
        self.kiwoom.OnEventConnect.connect(self.event_connect)

        self.setWindowTitle("계좌 정보")
        self.setGeometry(300, 300, 300, 150)

        btn1 = QPushButton("계좌 얻기", self)
        btn1.move(190, 20)
        btn1.clicked.connect(self.btn1_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 60, 280, 80)

    def btn1_clicked(self):
        account_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
        self.text_edit.append("계좌번호: " + account_num.rstrip(';'))

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("로그인 성공")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
'''






'''
from pykiwoom.kiwoom import *


#키움 openapi연결
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

#주식계좌
accounts = kiwoom.GetLoginInfo("ACCNO")
stock_account = accounts[0]

#ai가 선정한 종목리스트를 받아와 저장
code_list = open('c:\\Users\\김정수\\Desktop\\list.txt', 'rt')
code = code_list.readlines()
buy_sell=[] #주문 한줄씩 들어간 최종리스트
for i in code:
    i = i.replace("\n", "")
    i = i.split(" ")
    buy_sell.append(i)

for i in buy_sell:
    df = kiwoom.block_request("opt10080",
                          종목코드=i[0],
                          틱범위=1,
                          수정주가구분=0,
                          output="주식분봉차트조회",
                          next=0)
    print(df)
    df.to_csv('C:\\Users\\김정수\\Desktop\\{}.csv'.format(i[0]), encoding='euc-kr', header=True, index=None)#한글인코딩, 맨위의 헤더x


'''
'''
#ai가 선정한 종목리스트를 받아와 저장
code_list = open('c:\\Users\\김정수\\Desktop\\list.txt', 'rt')
code = code_list.readlines()
buy_sell=[] #주문 한줄씩 들어간 최종리스트
for i in code:
    i = i.replace("\n", "")
    i = i.split(" ")
    buy_sell.append(i)
'''

'''
#주식계좌
accounts = kiwoom.GetLoginInfo("ACCNO")
stock_account = accounts[0]
'''

'''
#매 종목마다 그대로 주문넣기
num = 0
def order(num):
    num = num
    kiwoom.SendOrder("매도", "0101", stock_account, 매수매도, 종목코드, 갯수, 금액, "00", "")
    num = num + 1
    kiwoom.SendOrder("매도", "0101", stock_account, 매수매도, 종목코드, 갯수, 금액, "00", "")
    num = num + 1
    kiwoom.SendOrder("매도", "0101", stock_account, 매수매도, 종목코드, 갯수, 금액, "00", "")
    num = num + 1
    kiwoom.SendOrder("매도", "0101", stock_account, 매수매도, 종목코드, 갯수, 금액, "00", "")
    num = num + 1
    kiwoom.SendOrder("매도", "0101", stock_account, 매수매도, 종목코드, 갯수, 금액, "00", "")
    num = num + 1
    if num == 50:
        num = 0
    return num
'''



'''
#주식계좌
accounts = kiwoom.GetLoginInfo("ACCNO")
stock_account = accounts[0]

#지정가 매수(삼전)
kiwoom.SendOrder("매수", "0101", stock_account, 1, "005930", 갯수, 금액, "00", "")

#지정가 매도(삼전)
kiwoom.SendOrder("매도", "0101", stock_account, 2, "005930", 갯수, 금액, "00", "")
#순서대로 주문이름, 화면번호, 계좌번호, 주문유형(1: 매수, 2: 매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도 정정), 매매할종목코드, 주문수량, 주문단가, 지정가(00)/시장가(03), 원주문번호로 주문정정시사용
'''
'''
import random
event_code = ['265520', '035760', '058820', '028150', '035900', '035600', '060720', '060250', '030190', '178920', '218410', '036540', '036490', '098460', '215000', '078130', '092730', '007390', '033640', '194700', '144510', '031390', '119860', '032190', '068240', '045390', '078600', '213420', '100130', '086450', '005290', '025900', '060570', '141080', '294140', '058470', '267980', '215200', '235980', '086900', '078160', '140410', '018290', '090460', '082920', '143240', '000250', '038500', '038540', '089980', '006730', '092190', '046890', '178320', '268600', '068760', '091990', '357780', '036830', '192440', '253450', '243840', '108320', '222080', '096530', '025980', '092040', '084850', '067160', '053800', '065660', '131370', '196170', '101490', '056190', '041510', '052020', '237690', '298380', '088800', '028300', '067630', '239610', '230360', '086520', '247540', '183490', '182400', '061970', '290650', '066970', '097520', '039200', '048260', '138080', '122990', '122870', '240810', '104830', '030530', '069080', '044340', '112040', '078070', '023410', '084370', '263050', '272290', '078020', '102710', '039030', '035810', '060150', '048530', '095700', '204270', '036930', '115450', '085660', '278280', '293490', '042000', '078340', '214370', '032500', '290510', '041960', '029960', '033290', '200130', '083790', '214150', '237880', '095610', '200230', '108230', '064760', '034230', '214450', '091700', '263750', '022100', '137400', '003380', '034950', '084990', '048410', '052260', '243070', '145020']
samplelist=random.sample(event_code, 50)
print(samplelist)
print(len(samplelist))
'''

'''
import pandas as pd

dfs = []
for i in range(50):
    df = pd.DataFrame( ... )
    # ...
    dfs.append(df)
'''





'''
import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5.QtCore import *
import datetime
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

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