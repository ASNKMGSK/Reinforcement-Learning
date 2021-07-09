import sys
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
from configparser import ConfigParser
from datetime import datetime as dt
import json
import logging
import logging.config
from util.utilities_logic import LoggerAdapter
# database define
from string_def import *

import creon_cpcomm     as com
import creon_cpdata     as CpData
import creon_cpdatafut  as CpDataFut
import creon_cpevent    as CpEvent
import creon_cpmariadb  as CpDB
import creon_cpodr      as CpOdr
import tcp_client       as TcpClient
import global_def       as gd

###############################################################################
# 테스트를 위한 메인 화면
class CpDataWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        # 시세종목
        #self.codelist = ['A05930', 'A151860']
        self.codelist = ['A151860']

        #####################################################################
        # logger
        self.logger = logging.getLogger("my_setting")
        self.logger = LoggerAdapter(CpDataWindow.__name__, self.logger)

        self.logger.debug(f'CpDataWindow Start')

        #####################################################################
        # db object
        self.objDB = CpDB.CpDB()

        #####################################################################
        # 이동평균
        self.cntTick = 0
        self.stkCur = []
        self.futCur = []
        self.stkShortOdrTP = 'N'
        self.stkLongOdrTP = 'N'

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
    # thread 3개 생성시 3개 동시 업데이트 됨
    def monitorCurPriceChange(self):

        print("=====================================================")
        print("monitorCurPriceChange ", self.stkCurData.item, self.stkCurData.item_nm, self.stkCurData.close)
        print("=====================================================")

        self.cntTick = self.cntTick + 1
        self.stkCur.append(self.stkCurData.close)
        self.stkCurnp = np.array(self.stkCur, dtype=float) # double ->float

        # 틱갯수로 이동평균 / self.futCurnp.shape 배열갯수
        if self.cntTick >= 20 and self.cntTick % 20 == 0:
            tama5   = ta.MA(self.stkCurnp,   5)
            tama5   = np.nan_to_num(tama5)

            tama10  = ta.MA(self.stkCurnp,  10)
            tama10 = np.nan_to_num(tama10)

            tama20  = ta.MA(self.stkCurnp,  20)
            tama20 = np.nan_to_num(tama20)

            tama60  = ta.MA(self.stkCurnp,  60)
            tama60 = np.nan_to_num(tama60)

            tama120 = ta.MA(self.stkCurnp, 120)
            tama120 = np.nan_to_num(tama120)

            tama240 = ta.MA(self.stkCurnp, 240)
            tama240 = np.nan_to_num(tama240)

            #tastddev = ta.STDDEV(self.stkCurnp)

            strtgyData = CpOdr.StrtgyData()

            strtgyData.ymd = com.dtymd
            strtgyData.strtgy_no = 100
            strtgyData.item = self.stkCurData.item
            strtgyData.tp     = 'T'
            strtgyData.term   = 20
            strtgyData.ma5    = float(tama5[-1])
            strtgyData.ma10   = float(tama10[-1])
            strtgyData.ma20   = float(tama20[-1])
            strtgyData.ma60   = float(tama60[-1])
            strtgyData.ma120  = float(tama120[-1])
            strtgyData.ma240  = float(tama240[-1])
            #strtgyData.vol_avg = 0
            #strtgyData.vol_std = tastddev[-1]

            self.objDB.stkindt('I', strtgyData, strtgyData)

            self.logger.error(f"CUR {tama5[-1]} {tama20[-1]} {tama5[-1]/tama20[-1]} {tama60[-1]/tama20[-1]}")

            ###############################################################################
            # 매수 주문
            # 잔고 보유 여부 확인
            # 5일선이 20일선 보다 10% 이하 만큼 높은 경우
            if tama5[-1] > tama20[-1] and tama5[-1]/tama20[-1] <= 1.1 and self.stkLongOdrTP == 'N':
                print("if self.cntTick >= 100 and self.cntTick % 20 == 0: ", self.cntTick, type(self.stkCurnp), self.stkCurnp.shape, self.stkCurnp.mean(), tama5[-1], tama20[-1], tama60[-1], tama120[-1])

                strtgyData.qty       = 1
                strtgyData.prc       = self.stkCurData.close
                strtgyData.odr_tp    = '2'
                strtgyData.stgy_msg  = '매수 : ' + str(tama5[-1])+' '+str(tama20[-1])+' '+str(tama60[-1])+' '+str(tama120[-1])+' '+self.stkLongOdrTP

                self.objDB.stkstrtgy('I', strtgyData, strtgyData)
                self.stkLongOdrTP = 'Y'

            ###############################################################################
            # 매도
            # 필히 잔고 유무 확인
            # 20일선이 60일선 보다 10% 낮게 있는 경우 매도
            # TRD.STKCON 확인, 종목이 여러개 인 경우 실시간 잔고 조회
            if  tama20[-1] < tama60[-1] and tama60[-1]/tama20[-1] >= 1.1 and self.stkShortOdrTP == 'N':
                strtgyData.qty = 1
                strtgyData.prc = self.stkCurData.close
                strtgyData.odr_tp = '1'
                strtgyData.stgy_msg = '매도 : ' + str(tama5[-1])+' '+str(tama20[-1])+' '+str(tama60[-1])+' '+str(tama120[-1])+' '+self.stkShortOdrTP

                self.objDB.stkstrtgy('I', strtgyData, strtgyData)
                self.stkShortOdrTP = 'Y'

                print("if self.cntTick >= 100 and self.cntTick % 20 == 0: ", self.cntTick, type(self.stkCurnp), self.stkCurnp.shape, self.stkCurnp.mean(), tama5[-1], tama20[-1], tama60[-1], tama120[-1])

        print(self.cntTick, type(self.stkCurnp), self.stkCurnp.shape, self.stkCurnp.mean())

        self.objDB.stkcurt('I', self.stkCurData, self.stkCurData)

        #COLUMNS_CHART_DATA = ['date', 'open', 'high', 'low', 'close', 'volume']

        ###############################################################################
        # 강화학습 통신
        # self.objTcpClient = TcpClient.TcpClient()
        # send_list = [self.stkCurData.ymd,
        #              self.stkCurData.open,
        #              self.stkCurData.high,
        #              self.stkCurData.low,
        #              self.stkCurData.close,
        #              self.stkCurData.acc_vol
        #              ]
        # req_data = {
        #     gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
        #     gd.KEY_NM_DATA: send_list
        # }
        #
        # self.objTcpClient.tcpClient(req_data)
        
        return

    ###############################################################################
    # self.parent.monitorTickChange()
    def monitorTickChange(self):

        (self.stkTickData.ask_vwap, self.stkTickData.bid_vwap, self.stkTickData.mid_vwap, self.stkTickData.mid_prc, self.stkTickData.prc_diff) = com.getFutVwap(self.stkTickData)

        print("*****************************************************")
        print("monitorTickChange ", self.stkTickData.ask_num[0], self.stkTickData.ask_qty[0], self.stkTickData.ask_prc[0])
        print("monitorTickChange ", self.stkTickData.ask_vwap, self.stkTickData.bid_vwap, self.stkTickData.mid_vwap, self.stkTickData.mid_prc, self.stkTickData.prc_diff)
        print("*****************************************************")

        self.objDB.stktick('I', self.stkTickData, self.stkTickData)

        return

    ###############################################################################
    # stock subscribe
    # def Subscribe(self, item, stkCurData, parent):
    def itemSubscribe(self, item):
        # 실시간 통신 요청

        objSBCur = CpData.CpSBStockCur()
        objSBCur.Subscribe(item, self.stkCurData, self)

        objSBTick = CpData.CpSBStockBid()
        objSBTick.Subscribe(item, self.stkTickData, self)

    def dataRequest(self):
        # 실시간 현재가  요청
        self.objThread = {}
        self.objThreadFut = {}

        #############################################################
        cnt = len(self.codelist)
        for i in range(cnt):
            item = self.codelist[i]
        
            # thread 미사용
            self.itemSubscribe(item)
            time.sleep(1)
        
            # thread 사용
            # self.objThread[item] = threading.Thread(target=self.itemSubscribe, args=(item,))
            # self.objThread[item].start()
            # time.sleep(1)

        #codelist = CpData.StkDataHist()
        #self.objDB.stkmsttgt('S', codelist, codelist)
        #cnt = len(codelist.item)
        #for i in range(cnt):
        #    item_list = list(codelist.item[i])
        #    item = item_list[0]
        #    print(cnt, item, item_list, type(item_list))
        #
        #    self.itemSubscribe(item)
        #    time.sleep(1)

        # codelistf = ['101P3','101P6']
        # cntf = len(codelistf)
        # for i in range(cntf):
        #     itemf = codelistf[i]
        #
        #     # thread 미사용
        #     self.itemFutSubscribe(itemf)
        #     time.sleep(1)
        # #
        # #     self.objThreadFut[itemf] = threading.Thread(target=self.itemFutSubscribe, args=(itemf,))
        # #     self.objThreadFut[itemf].start()
        # #     time.sleep(1)

    # 투자자정보
    def btnInv_clicked(self):
        return

    # 매수 주문
    def btnBuy_clicked(self):

        self.dataRequest()

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

    # 정정주문
    def btnModify_clicked(self):

        return

    # 취소주문
    def btnCancel_clicked(self):
        return

    # 종료
    def btnExit_clicked(self):
        exit()

    # 종목정보
    def btnMst_clicked(self):

        return


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) == 1:
        print("옵션을 주지 않고 이 스크립트를 실행하셨군요")

    # #print("옵션 개수: %d %s %s" % (len(sys.argv) - 1, sys.argv[0], sys.argv[1]))
    #
    # #사용자 정보
    # cp_exe = com.CreonPlusExecuter()
    # cp_exe.set_file_path(cipher_path="user_info.txt", key_path="key.txt")
    # user_info = cp_exe.get_user_info()
    #
    # if user_info is None:
    # 	print("사용자 정보가 없습니다.")
    # 	sys.exit()
    #
    # # CreonPlus 실행
    # if not cp_exe.execute_cp(user_info):
    # 	logging.critical("프로그램 종료")
    # 	sys.exit()

    with open("setting/logging.json", 'rt') as f:
        log_config = json.load(f)
    today = dt.today().strftime("%Y%m%d")
    log_config['handlers']['info_file_handler']['filename'] = f'../LOG/cpdata.{today}'
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("my_setting")

    logger.debug("Start")

    myWindow = CpDataWindow()
    myWindow.show()
    myWindow.dataRequest()

    app.exec_()