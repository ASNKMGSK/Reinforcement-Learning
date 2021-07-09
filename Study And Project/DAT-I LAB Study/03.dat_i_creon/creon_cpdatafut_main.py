import sys
import os
from PyQt5.QtWidgets import *
import win32com.client
from enum import Enum
from time import sleep
import threading
import pythoncom
import time
import asyncio
import queue
import numpy as np
import talib as ta
import pymysql

import creon_cpcomm     as com
import creon_cpdata     as CpData
import creon_cpdatafut  as CpDataFut
import creon_cpevent    as CpEvent
import creon_cpmariadb  as CpDB
import creon_cpodr      as CpOdr

###############################################################################
# 테스트를 위한 메인 화면
class MyWindow(QMainWindow):
    def __init__(self):
        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()
        if com.InitTradeInit() == False:
            exit()

        #####################################################################
        #  account info
        self.acc_no = com.g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.acc_tp = com.g_objCpTrade.GoodsList(self.acc_no, 1)  # 주식상품 구분

        #####################################################################
        #  stock object
        self.stkCurData = CpData.StkCurData()
        self.stkTickData = CpData.StkTickData()  # 주문 현재가/10차 호가 저장

        self.objSBCur = CpData.CpSBStockCur()
        self.objSBid = CpData.CpSBStockBid()

        #####################################################################
        # future object
        self.futCurData = CpDataFut.FutCurData()
        self.objSBCurFut = CpDataFut.CpFutureCurOnly()

        self.futTickData = CpDataFut.FutTickData()

        #####################################################################
        # db object
        self.objDB = CpDB.CpDB()

        #####################################################################
        # db object
        self.cntTick = 0
        self.stkCur  = []
        self.futCur = []

        super().__init__()
        self.setWindowTitle(sys.argv[0])
        self.setGeometry(300, 300, 300, 700)
        nH = 20

        btnBuy = QPushButton("종목 분 데이터 조회", self)
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

    ###############################################################################
    # 주식 현재가 업데이트
    def monitorCurPriceChange(self):
        # print("=====================================================")
        # print("monitorCurPriceChange ", self.stkCurData.item, self.stkCurData.item_nm, self.stkCurData.close)
        # print("=====================================================")

    #   self.objDB.stkcurt('I', self.stkCurData, self.stkCurData)

        return


    #https: // ntguardian.wordpress.com / 2018 / 07 / 17 / stock - data - analysis - python - v2 /
    ###############################################################################
    # 선물 현재가 업데이트
    def monitorCurPriceChangeFut(self):
        print("=====================================================")
        print("monitorCurPriceChangeFut ", self.futCurData.item, self.futCurData.close, self.futCurData.acc_vol)
        print("=====================================================")

    #    self.cntTick = self.cntTick + 1
    #    self.futCur.append(self.futCurData.close)
    #    self.futCurnp = np.array(self.futCur)
    #
    #    # self.futCurMa["20d"] = np.round(self.futCurnp.rolling(window=20, center=False).mean(), 2)
    #
    #    # 틱갯수로 이동평균 / self.futCurnp.shape 배열갯수
    #    tama5   = ta.MA(self.futCurnp,   5)
    #    tama20  = ta.MA(self.futCurnp,  20)
    #    tama60  = ta.MA(self.futCurnp,  60)
    #    tama120 = ta.MA(self.futCurnp, 120)
    #
    #    print(self.cntTick, type(self.futCurnp), self.futCurnp.shape, self.futCurnp.mean(), tama5[-1], tama20[-1], tama60[-1], tama120[-1])
    #
    #    self.objDB.futcurt('I', self.futCurData, self.futCurData)

        return

    def monitorIndexChange(self):

        #print("*****************************************************")
        #print("monitorIndexChange ", self.stkCurData.item, self.stkCurData.item_nm, self.stkCurData.close)
        #print("*****************************************************")
        
    #    con = pymysql.connect(host='localhost', port=3316, user='root', passwd='root', db='MySql', charset='utf8', autocommit=False)
    #    self.objDB.stkidxt('I', con, self.stkCurData, self.stkCurData)

        return

    # creon_cpevent.py 호출
    def monitorTickChangeFut(self):

        (self.futTickData.ask_vwap, self.futTickData.bid_vwap, self.futTickData.mid_vwap, self.futTickData.mid_prc, self.futTickData.prc_diff) = com.getFutVwap(self.futTickData)

        print("*****************************************************")
        print("monitorTickChangeFut ", self.futTickData.ask_num[0], self.futTickData.ask_qty[0], self.futTickData.ask_prc[0])
        print("monitorTickChangeFut ", self.futTickData.ask_vwap, self.futTickData.bid_vwap, self.futTickData.mid_vwap, self.futTickData.mid_prc, self.futTickData.prc_diff)
        print("*****************************************************")

        self.objDB.futtick('I', self.futTickData, self.futTickData)

        return

    ###############################################################################
    # stock subscribe
    # def Subscribe(self, item, stkCurData, parent):
    def itemSubscribe(self, item):
        # 실시간 통신 요청

        objSBCur = CpData.CpSBStockCur()
        objSBCur.Subscribe(item, self.stkCurData, self)

    ###############################################################################
    # future subscribe
    def itemFutSubscribe(self, item):
        # 실시간 통신 요청

        objSBCurFut = CpDataFut.CpFutureCurOnly()
        objSBCurFut.Subscribe(item, self.futCurData, self)

        objSBTickFut = CpDataFut.CpSBFutureJpBid()
        objSBTickFut.Subscribe(item, self.futTickData, self)

    ###############################################################################
    # index subscribe
    def IdxSubscribe(self, item):
        # 실시간 통신 요청

        print(item)

        objSBIndexIS = CpData.CpSBStockIndexIS()
        objSBIndexIS.Subscribe(item, self.stkCurData, self)

    ###############################################################################
    # 투자자정보 request
    # object를 인자로 넘겨서 해결
    def ivtRequest(self):
        pythoncom.CoInitialize()

        objDBRQ = CpDB.CpDB()
        con = objDBRQ.connect()
        print("con", con)

        objIvt = CpData.Cp7222()

        while True:
            remainCount = com.g_objCpStatus.GetLimitRemainCount(1)  # 1 시세 제한
            if remainCount <= 0:
                print('시세 연속 조회 제한 회피를 위해 sleep', com.g_objCpStatus.LimitRequestRemainTime)
                time.sleep(com.g_objCpStatus.LimitRequestRemainTime / 1000)

            objIvtData = CpData.Ivt7222()
            objIvt.Request(objIvtData)

            objDBRQ.tivtt(con, 'I', objIvtData, objIvtData)

            time.sleep(10)

        return

    ###############################################################################
    # stock request
    # thread 사용하여 여러종목 request 사용시 에러
    # object를 인자로 넘겨서 해결
    def itemRequest(self, item):

        print(item)
        pythoncom.CoInitialize()

        objIdx = CpData.CpMarketEye2()
        objMktEye = win32com.client.Dispatch("CpSysDib.MarketEye")

        objDBRQ = CpDB.CpDB()
        con = objDBRQ.connect()
        print("con", con)

        for i in range(10000):
            stkCurDataIdx = CpData.StkCurData()

            remainCount = com.g_objCpStatus.GetLimitRemainCount(1)  # 1 시세 제한
            if remainCount <= 0:
                print('시세 연속 조회 제한 회피를 위해 sleep', com.g_objCpStatus.LimitRequestRemainTime)
                time.sleep(com.g_objCpStatus.LimitRequestRemainTime / 1000)

            objIdx.Request(objMktEye, item, stkCurDataIdx)
            print(stkCurDataIdx.item, stkCurDataIdx.item_nm, stkCurDataIdx.close)

            self.objDBRQ.stkidxt('I', con, stkCurDataIdx, stkCurDataIdx)

            time.sleep(3)

        return

    #############################################################################
    # error
    # raise err.InterfaceError
    # pymysql.err.InterfaceError
    def dataRequest(self):
        # 실시간 현재가  요청
        self.objThread = {}
        self.objThread1 = {}
        self.objThreadFut = {}

        #############################################################
        # DB list -> python list 변경
        # codelist = ['U001', 'U002','U003','U004','U180']
        # cnt = len(codelist)
        # for i in range(cnt):
        #     item = codelist[i]
        #     self.objThread[item] = threading.Thread(target=self.itemRequest, args=(item,))
        #     self.objThread[item].start()
        #     time.sleep(1)

        #############################################################
        # 투자자 매매추이
    #    self.objThreadivt = {}
    #    itemivt = 'A'
    #    self.objThreadivt[itemivt] = threading.Thread(target=self.ivtRequest)
    #    self.objThreadivt[itemivt].start()
    #    time.sleep(1)
    #
    #    objDBRQ = CpDB.CpDB()
    #    con = objDBRQ.connect()
    #    print("con", con)
    #
    #    codelist = CpData.StkDataHist()
    #    self.objDB.stkidxmst('S', con, codelist, codelist)
    #    cnt = len(codelist.item)
    #    for i in range(cnt):
    #        item_list = list(codelist.item[i])
    #        item = item_list[0]
    #        print(cnt, item, item_list, type(item_list))
    #        # thread 미사용
    #        self.IdxSubscribe(item)
    #        time.sleep(0.1)
    #
    #    con.close()

        # codelistf = ['U001', 'U002','U003','U004','U180']
        # cntf = len(codelistf)
        # for i in range(cntf):
        #     itemf = codelistf[i]
        #
        #     # thread 미사용
        #     self.IdxSubscribe(itemf)
        #     time.sleep(1)


        codelistf = ['101Q9']
        cntf = len(codelistf)
        for i in range(cntf):
            itemf = codelistf[i]

            # thread 미사용
            self.itemFutSubscribe(itemf)
            time.sleep(0.1)

            # subscribe thread use error
            # self.objThreadFut[itemf] = threading.Thread(target=self.itemFutSubscribe, args=(itemf,))
            # self.objThreadFut[itemf].start()
            # time.sleep(1)

    # 투자자정보
    def btnInv_clicked(self):
        return

    # 매수 주문
    def btnBuy_clicked(self):

    #    self.dataRequest()

        # #####################################################################
        # # 전략, 체결
        # # def Request(self, item, sel_tp, term, count, start_ymd, end_ymd, hist):
        # # sel_tp : 1 기간, 2 개수
        # self.stkDataHist    = CpData.StkDataHist()
        # self.objStockChart  = CpData.CpStockChart()
        # ymd = com.dtymd
        # if self.objStockChart.Request('A005930', '1', 'T', 100000, ymd, ymd, self.stkDataHist) == False:
        #     exit()
        #
        # # cnt = len(self.stkDataHist.ymd)
        # # for i in range(0, cnt, 1):
        # #     if i < 100 :
        # #         print("self.objStockChart.Request > ", cnt, i, self.stkDataHist.ymd[i], self.stkDataHist.time[i], self.stkDataHist.open[i])
        #
        # i=0
        # cnt = len(self.stkDataHist.ymd)
        # print("self.objStockChart.Request > ", cnt, i, self.stkDataHist.ymd[i], self.stkDataHist.time[i],              self.stkDataHist.open[i])
        #
        # self.objDB.stkcurt('I', self.stkDataHist, self.stkDataHist)
        #
        # return
        
        return
    # 정정주문
    def btnModify_clicked(self):

        return

    # 취소주문
    def btnCancel_clicked(self):
        return

    # 종료
    def btnExit_clicked(self):
        os._exit(1)
        sys.exit()

    # 종목정보
    def btnMst_clicked(self):

        return


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) is 1:
        print("옵션을 주지 않고 이 스크립트를 실행하셨군요")

    #print("옵션 개수: %d %s %s" % (len(sys.argv) - 1, sys.argv[0], sys.argv[1]))

    myWindow = MyWindow()
    myWindow.show()
    myWindow.dataRequest()

    app.exec_()