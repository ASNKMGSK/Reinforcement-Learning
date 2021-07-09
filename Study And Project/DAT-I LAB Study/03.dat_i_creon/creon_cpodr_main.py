import sys
import signal
from PyQt5.QtWidgets import *
import win32com.client
from enum import Enum
from time import sleep
import threading
import pythoncom
import time
import asyncio
import queue

from configparser import ConfigParser
from datetime import datetime as dt
import json
import logging
import logging.config
from util.utilities_logic import LoggerAdapter

import creon_cpcomm     as com
import creon_cpdata     as CpData
import creon_cpdatafut  as CpDataFut
import creon_cpevent    as CpEvent
import creon_cpmariadb  as CpDB
import creon_cpodr      as CpOdr

###############################################################################
# 테스트를 위한 메인 화면
class CpOdrWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pythoncom.CoInitialize()

        self.odrExec0 = CpOdr.CpOrderExec()
        self.odrExec1 = CpOdr.CpOrderExec()
        self.odrExec2 = CpOdr.CpOrderExec()
        self.odrExec3 = CpOdr.CpOrderExec()

        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()
        if com.InitTradeInit() == False:
            exit()

        self.acc_no = com.g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.acc_tp = com.g_objCpTrade.GoodsList(self.acc_no, 1)  # 주식상품 구분

        #####################################################################
        # logger
        self.logger = logging.getLogger("my_setting")
        self.logger = LoggerAdapter(CpOdrWindow.__name__, self.logger)

        self.logger.debug(f'CpOdrWindow Start {self.acc_no} {self.acc_tp}')
        #####################################################################
        # 전략, 체결
        self.strtgyData  = CpOdr.StrtgyData()

        #####################################################################
        # 체결 data class
        self.stkConData = CpOdr.StkConData()
        self.objSBCon = CpOdr.CpSBConclusion()

        #####################################################################
        # 체겷 Subscribe
        # def monitorCon(self): 실시간 업데이트
        self.objSBCon.Subscribe(self.stkConData, self)

        #####################################################################
        # 잔고
        self.objBlnc     = CpOdr.Cp6033()

        #####################################################################
        #  stock object
        self.stkCurData = CpData.StkCurData()
        self.stkTickData = CpData.StkTickData()  # 주문 현재가/10차 호가 저장

        self.objSBCur = CpData.CpSBStockCur()
        self.objSBbid = CpData.CpSBStockBid()

        #####################################################################
        # db object
        self.objDB = CpDB.CpDB()

        self.setWindowTitle("PLUS API TEST")
        self.setGeometry(300, 300, 300, 700)
        nH = 20

        btnBuy = QPushButton("매수/매도 주문", self)
        btnBuy.move(20, nH)
        # btnBuy.resize(200,30)
        btnBuy.clicked.connect(self.btnBuy_clicked)

        nH += 50
        btnExit = QPushButton("종료", self)
        btnExit.move(20, nH)
        # btnExit.resize(200,30)
        btnExit.clicked.connect(self.btnExit_clicked)

        nH += 50
        btnMst = QPushButton("기본정보", self)
        btnMst.move(20, nH)
        # btnExit.resize(200,30)
        btnMst.clicked.connect(self.btnMst_clicked)

        nH += 50
        btnInv = QPushButton("투자자종합", self)
        btnInv.move(20, nH)
        btnInv.clicked.connect(self.btnInv_clicked)

    def monitorCurPriceChange(self):
        print("=====================================================")
        print("monitorCurPriceChange ", self.stkCurData.item, self.stkCurData.item_nm, self.stkCurData.close)
        print("=====================================================")

        self.objDB.stkcurt('I', self.stkCurData, self.stkCurData)

        return

    ###############################################################################
    # 체결 정보 업데이트
    # 클래스 실행 하는 곳이 아님 실행 되는 클래스에서 업데이트
    def monitorCon(self):

        print("=====================================================")
        print("monitorCon ", self.stkConData.item, self.stkConData.blnc_qty, self.stkConData.con_prc, self.stkConData.strtgy_no)
        print("=====================================================")

        self.objDB.stkcon('I', self.stkConData, self.stkConData)

        # 체결 데이터인 경우
        if self.stkConData.con_tp == '1': #체결
            ###############################################################################
            # creon_cpodr.py : 정상 주문시 insert
            # 체결시 주문내역 업데이트
            self.objDB.stkodr('U', self.stkConData, self.stkConData)

            ###############################################################################
            # 잔고 정보 업데이트
            self.stkBlncData = CpOdr.StkBlncData()
            self.odrExec0.getBlncData('S', self.acc_no, self.stkBlncData)
            self.objDB.stkblnc('I', self.stkBlncData, self.stkBlncData)


        return

    # 투자자정보 잔고 테스트
    def btnInv_clicked(self):

        # creon_cpodr.py
        self.stkBlncData = CpOdr.StkBlncData()
        self.odrExec0.getBlncData('S', self.acc_no, self.stkBlncData)

        cnt = len(self.stkBlncData.acc_no)
        print("BLNC CNT", cnt)

        for i in range(cnt):
            self.logger.debug(f' {self.stkBlncData.acc_no[i]} {self.stkBlncData.item[i]}')

        self.objDB.stkblnc('I', self.stkBlncData, self.stkBlncData)

        # self.investor = CpData.CpInvestor()
        # self.investor.Request()
        #
        # self.SBinvestor = CpData.CpSBInvestor()
        # self.SBinvestor.Subscribe("001", self)

        return

    def my_coroutine(self, task_name, seconds_to_sleep=3):
        print('{0} sleeping for: {1} seconds'.format(task_name, seconds_to_sleep))
        time.sleep(seconds_to_sleep)
        print('{0} is finished'.format(task_name))

    ###############################################################################
    # stock subscribe
    def item_subscribe(self, item):
        # 실시간 통신 요청

        self.objSBCur.Subscribe(item, self.stkCurData, self)

    ###############################################################################
    #
    def item_request(self, item, tt):

        pythoncom.CoInitialize()

        print("def item_request(self, item):")

        # print('#####################################')
        # objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")
        # objStockMst.SetInputValue(0, code)
        # objStockMst.BlockRequest()
        # print('BlockRequest 로 수신 받은 데이터')
        # item = {}
        # item['현재가'] = objStockMst.GetHeaderValue(11)  # 종가
        # item['대비'] = objStockMst.GetHeaderValue(12)  # 전일대비
        # print(item)

        objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")

        while True:
            if self.objCurBid2.Request(objStockMst, item, self.stkTickData) == False:
                print("현재가 통신 실패")

            time.sleep(tt)

        # aa = CpData.CpSBStockCurBid()
        # objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")
        # aa.Subscribe(objStockMst, item, self.stkTickData, self)
        #
        # print("self.stkTickData.cur", self.stkTickData.cur)

    #J57DM09
    def btnBuy_clicked(self):
        t4 = threading.Thread(target=self.odrExec3.order_thread,   args=(self.acc_no,))
        t4.start()

    # 정정주문
    def btnModify_clicked(self):
        self.bsMonitor()

        # self.odrExec.ModifyOrder()
        return

    # 취소주문
    def btnCancel_clicked(self):
        # self.odrExec.CancelOrder()
        return

    # 종료
    def btnExit_clicked(self):
        exit()

    # 종목정보
    def btnMst_clicked(self):
        # self.stockMst = CpData.CpStockMst()
        # self.stockMst.Request("A005930")

        self.dicOdrList = {}
        self.odrList    = CpOdr.StkUnConData()
        self.odrExec0.canorder_async(self.acc_no, self.dicOdrList, self.odrList)

        cnt = len(self.odrList.item)
        for i in range(cnt):
            print("주문정보 : %s, %s" % (self.odrList.item[i], self.odrList.item_nm[i]))

        return

    def signal_handler(signal, frame):  # SIGINT handler정의
        print('You pressed Ctrl+C!')
        sys.exit(0)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    with open("setting/logging.json", 'rt') as f:
        log_config = json.load(f)
    today = dt.today().strftime("%Y%m%d")
    log_config['handlers']['info_file_handler']['filename'] = f'../LOG/cpodr.{today}'
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("my_setting")

    logger.debug("Start")

    myWindow = CpOdrWindow()

    signal.signal(signal.SIGINT, myWindow.signal_handler)  # 등록
    print('Press Ctrl+C')

    myWindow.show()

    #myWindow.btnBuy_clicked()

    app.exec_()