# -*- coding: utf-8 -*-
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
import pandas as pd
import os
from configparser import ConfigParser
from datetime import datetime as dt
import json
import logging
import logging.config
from util.utilities_logic import LoggerAdapter

import creon_cpcomm as com
import creon_cpdata  as CpData
import creon_cpevent as CpEvent
import creon_cpmariadb  as CpDB 
import creon_cpodr      as CpOdr

#cpdb oracle include
#import creon_cpdb    as CpDB


import tcp_client as TcpClient
import global_def as gd
from configparser import ConfigParser
import select
from datetime import datetime as dt
from datetime import timedelta
from time import sleep
 
class CpStockChart:
    def __init__(self):
        super().__init__()
        self.objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

        #####################################################################
        # logger
        self.logger = logging.getLogger("my_setting")
        self.logger = LoggerAdapter(CpStockChart.__name__, self.logger)
        self.logger.debug(f'CpStockChart Start')

        #6:전일대비(long or float) - 주) 대비부호(37)과반드시같이요청해야함
        self.rqField = [0, 2, 3, 4, 5, 6, 8, 37]  # 요청 필드
        
    # 차트 요청 - 기간 기준으로
    def RequestFromTo(self, code, fromDate, toDate, caller):
        print(code, fromDate, toDate)
        
        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()
 
        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('1'))  # 기간으로 받기
        self.objStockChart.SetInputValue(2, toDate)  # To 날짜
        self.objStockChart.SetInputValue(3, fromDate)  # From 날짜
        #self.objStockChart.SetInputValue(4, 500)  # 최근 500일치
        self.objStockChart.SetInputValue(5, self.rqField)  # 날짜,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, ord('D'))  # '차트 주기 - 일간 차트 요청
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.objStockChart.BlockRequest()
 
        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
 
        len = self.objStockChart.GetHeaderValue(3)
        sign = self.objStockChart.GetHeaderValue(8)
        
        print("수신갯수", len, "부호", chr(sign))
        
        caller.dates = []
        caller.opens = []
        caller.highs = []
        caller.lows = []
        caller.closes = []
        caller.vols = []
        caller.diff = []
        caller.sign = []
        caller.item = []
        
        # 요청필드 순서와 관계없음 
        # self.rqField = [0, 2, 3, 4, 5, 6, 8, 37]  # 요청 필드
        for i in range(len):
            caller.dates.append(self.objStockChart.GetDataValue(0, i))      # 0: 날짜(ulong)	                                
            caller.opens.append(self.objStockChart.GetDataValue(1, i))      # 2:시가(long or float)                            
            caller.highs.append(self.objStockChart.GetDataValue(2, i))      # 3:고가(long or float)	                            
            caller.lows.append(self.objStockChart.GetDataValue(3, i))       # 4:저가(long or float)	                            
            caller.closes.append(self.objStockChart.GetDataValue(4, i))     # 5:종가(long or float)	                            
            caller.diff.append(self.objStockChart.GetDataValue(5, i))        # 8:거래
            caller.vols.append(self.objStockChart.GetDataValue(6, i))       # 6:전일	                            
            #caller.sign.append(chr(self.objStockChart.GetDataValue(8, i)))  # 37:부호
            
            caller.item.append(code)
        
        print("수신갯수", len)
 
    # 차트 요청 - 최근일 부터 개수 기준
    def RequestDWM(self, code, dwm, count, caller):
        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()
 
        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, count)  # 최근 500일치
        self.objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 요청항목 - 날짜,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, dwm)  # '차트 주기 - 일/주/월
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.objStockChart.BlockRequest()
 
        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
 
        len = self.objStockChart.GetHeaderValue(3)
 
        caller.dates = []
        caller.opens = []
        caller.highs = []
        caller.lows = []
        caller.closes = []
        caller.vols = []
        caller.times = []
        caller.diff = []
        caller.sign = []

        for i in range(len):
            caller.dates.append(self.objStockChart.GetDataValue(0, i))      # 0: 날짜(ulong)	                                
            caller.opens.append(self.objStockChart.GetDataValue(1, i))      # 1:시간(long) - hhmm	                            
            caller.highs.append(self.objStockChart.GetDataValue(2, i))      # 2:시가(long or float)	                            
            caller.lows.append(self.objStockChart.GetDataValue(3, i))       # 3:고가(long or float)	                            
            caller.closes.append(self.objStockChart.GetDataValue(4, i))     # 4:저가(long or float)	                            
            caller.vols.append(self.objStockChart.GetDataValue(5, i))       # 5:종가(long or float)	                            
            caller.diff.append(self.objStockChart.GetDataValue(6, i))        # 6:전일대비(long or float) - 주) 대비부호(37)과반드시같이요청해야함
            caller.sign.append(chr(self.objStockChart.GetDataValue(37, i))) # 37:대비부호(char) - 수신값은 GetHeaderValue 8 대비부호와동일	
	
        print(len)
 
        return

    # 차트 요청 - 분간, 틱 차트
    def RequestMTT(self, code, dwm, count, caller):
        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()

        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, count)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, dwm)  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(7, 1)  # 분틱차트 주기
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        totlen = 0
        while True:
            self.objStockChart.BlockRequest()
            rqStatus = self.objStockChart.GetDibStatus()
            rqRet = self.objStockChart.GetDibMsg1()
            print("통신상태", rqStatus, rqRet)
            if rqStatus != 0:
                exit()

            len = self.objStockChart.GetHeaderValue(3)
            totlen += len

            print('날짜', '시간', '시가', '고가', '저가', '종가', '거래량')
            print("==============================================-")

            caller.dates = []
            caller.opens = []
            caller.highs = []
            caller.lows = []
            caller.closes = []
            caller.vols = []
            caller.times = []
            for i in range(len):
                caller.dates.append(self.objStockChart.GetDataValue(0, i))
                caller.times.append(self.objStockChart.GetDataValue(1, i))
                caller.opens.append(self.objStockChart.GetDataValue(2, i))
                caller.highs.append(self.objStockChart.GetDataValue(3, i))
                caller.lows.append(self.objStockChart.GetDataValue(4, i))
                caller.closes.append(self.objStockChart.GetDataValue(5, i))
                caller.vols.append(self.objStockChart.GetDataValue(6, i))

                print(totlen, len, self.objStockChart.Continue, caller.dates[i], caller.times[i])

            if (self.objStockChart.Continue == False):
                break
            if (totlen >= 100000000):
                break

    # 차트 요청 - 분간, 틱 차트
    def RequestMT(self, code, dwm, count, caller):
        # plus 상태 체크
        if com.InitPlusCheck() == False:
            exit()
 
        self.objStockChart.SetInputValue(0, code)  # 종목코드
        self.objStockChart.SetInputValue(1, ord('2'))  # 개수로 받기
        self.objStockChart.SetInputValue(4, count)  # 조회 개수
        self.objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량
        self.objStockChart.SetInputValue(6, dwm)  # '차트 주기 - 분/틱
        self.objStockChart.SetInputValue(7, 1)  # 분틱차트 주기
        self.objStockChart.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.objStockChart.BlockRequest()
 
        rqStatus = self.objStockChart.GetDibStatus()
        rqRet = self.objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
 
        len = self.objStockChart.GetHeaderValue(3)
 
        caller.dates = []
        caller.opens = []
        caller.highs = []
        caller.lows = []
        caller.closes = []
        caller.vols = []
        caller.times = []
        for i in range(len):
            caller.dates.append(self.objStockChart.GetDataValue(0, i))
            caller.times.append(self.objStockChart.GetDataValue(1, i))
            caller.opens.append(self.objStockChart.GetDataValue(2, i))
            caller.highs.append(self.objStockChart.GetDataValue(3, i))
            caller.lows.append(self.objStockChart.GetDataValue(4, i))
            caller.closes.append(self.objStockChart.GetDataValue(5, i))
            caller.vols.append(self.objStockChart.GetDataValue(6, i))

            #print(self.objStockChart.GetDataValue(0, i))            
            
#        df1 =pd.DataFrame("2018", columns=['일자'])
        
        data = {"date"  : caller.dates,
                "times" : caller.times,
                "closes" : caller.closes,
                }

        print(data) 
        
        df1 = pd.DataFrame(data, columns=['date','times','closes'])        
        print(df1)    
        print(len)
 
        ma5   = df1['closes'].rolling(window=5).mean()
        ma10  = df1['closes'].rolling(window=10).mean()
        ma20  = df1['closes'].rolling(window=20).mean()
        ma60  = df1['closes'].rolling(window=60).mean()
        ma120 = df1['closes'].rolling(window=120).mean()
        
        data_ma = {"ma5"  : ma5,
                   "ma10" : ma10,
                   "ma20" : ma20,
                }

        print(data_ma) 
        
        df_ma = pd.DataFrame(data_ma, columns=['ma5','ma10','ma20'])        
        
        print(df_ma)
        
        # 가격 비교
        # 매수
        # 체결내역확인
        # 잔고확인
        
        return
 
class CpChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
 
        # 기본 변수들
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.vols = []
        self.times = []
        self.diff = []
        self.sign = []
        self.item = []
        
        self.objChart = CpStockChart()
        
        from_day = dt.today() - timedelta(days=7)
        from_day = from_day.strftime("%Y%m%d")
        today = dt.today().strftime("%Y%m%d")
        
        # 윈도우 버튼 배치
        self.setWindowTitle("PLUS API TEST")
        nH = 20
 
        self.codeEdit = QLineEdit("", self)
        self.codeEdit.move(20, nH)
        self.codeEdit.setText('005930')
        self.codeEdit.textChanged.connect(self.codeEditChanged)
        self.label = QLabel('종목코드', self)
        self.label.move(140, nH)

        nH += 50
 
        btchart1= QPushButton("기간(일간) 요청", self)
        btchart1.move(20, nH)
        btchart1.clicked.connect(self.btchart1_clicked)

        self.fromdtEdit = QLineEdit("", self)
        self.fromdtEdit.setText(from_day)
        self.fromdtEdit.move(140, nH)

        self.todtEdit = QLineEdit("", self)
        self.todtEdit.setText(today)
        self.todtEdit.move(250, nH)

        self.tickEdit = QLineEdit("", self)
        self.tickEdit.setText("D")
        self.tickEdit.move(350, nH)

        self.fromdtEdit.textChanged.connect(self.fromdtEditChanged)
        self.todtEdit.textChanged.connect(self.todtEditChanged)
        self.tickEdit.textChanged.connect(self.tickEditChanged)

        nH += 50
 
        btchart2 = QPushButton("개수(일간) 요청", self)
        btchart2.move(20, nH)
        btchart2.clicked.connect(self.btchart2_clicked)
        nH += 50
 
        btchart3 = QPushButton("분차트 요청", self)
        btchart3.move(20, nH)
        btchart3.clicked.connect(self.btchart3_clicked)
        nH += 50
 
        btchart4 = QPushButton("틱차트 요청", self)
        btchart4.move(20, nH)
        btchart4.clicked.connect(self.btchart4_clicked)
        nH += 50
 
        btchart5 = QPushButton("주간차트 요청", self)
        btchart5.move(20, nH)
        btchart5.clicked.connect(self.btchart5_clicked)
        nH += 50
 
        btchart6 = QPushButton("월간차트 요청", self)
        btchart6.move(20, nH)
        btchart6.clicked.connect(self.btchart6_clicked)
        nH += 50
 
        btchart7 = QPushButton("엑셀로 저장", self)
        btchart7.move(20, nH)
        btchart7.clicked.connect(self.btchart7_clicked)
        nH += 50
 
        btnExit = QPushButton("종료", self)
        btnExit.move(20, nH)
        btnExit.clicked.connect(self.btnExit_clicked)
        nH += 50

        #####################################################################
        # UI size
        self.setGeometry(200, 400, 400, nH)

        #####################################################################
        # 초기값 설정
        self.setCode('005930')
        self.fromdt=self.fromdtEdit.text()
        self.todt=self.todtEdit.text()
        self.ticktp = self.tickEdit.text()

        #####################################################################
        # Tcp 통신
        """
        self.config = ConfigParser()
        self.config.read('config.ini')
        order = self.config['ORDER']
        print('order["IP"]', order["IP"], int(order["PORT"]))
        ord_form = (order["IP"], int(order["PORT"]))
        self.ord_sock = TcpClient.OrderPort(ord_form)
        """
        #####################################################################
        # Order
        # plus 상태 체크
        pythoncom.CoInitialize()
        if com.InitPlusCheck() == False:
            exit()
        if com.InitTradeInit() == False:
            exit()
        self.objOdr   = CpOdr.CpOrder()
        self.acc_no = com.g_objCpTrade.AccountNumber[0]  # 계좌번호
        
        #####################################################################
        # 체결
        self.stkConData = CpOdr.StkConData()
        self.objSBCon = CpOdr.CpSBConclusion()
        self.objSBCon.Subscribe(self.stkConData, self)

        #####################################################################
        # logger
        self.logger = logging.getLogger("my_setting")
        self.logger = LoggerAdapter(CpChartWindow.__name__, self.logger)
        self.logger.debug(f'CpChartWindow Start')

        print("CpChartWindow Start")
        
    # server 에서만 사용
    # input_ready, write_ready, except_ready = select.select(input_list, [], [])
    def recvloop(self):
        while True:
            try:
                pythoncom.CoInitialize()
                data = ''
                data = self.ord_sock.recv_pckt()
                print("recvloop", data[0], data[1], data[2], data[3])
                
                # 주문로직
                # def buyOrder(self, acc_no, item, qty, price, odata):
                item = data[1]
                qty = 1
                prc = data[3]
                ord_no = ''
                bResult = self.objOdr.buyOrder(self.acc_no, item, qty, prc, ord_no)
                if bResult == False:
                    print("주문 실패")
                    return        
            except Exception as e:
                print("except Exception as e", e)
                break
            
            
    # 기간(일간) 으로 받기
    def btchart1_clicked(self):

        pythoncom.CoInitialize()

        print("def btchart1_clicked(self) ", self.ticktp, self.code, self.fromdt, self.todt)

        if self.ticktp == 'D':
            if self.objChart.RequestFromTo(self.code, self.fromdt, self.todt, self) == False:
                exit()

        # 분봉 데이터
        if self.ticktp == 'M':
            if self.objChart.RequestMTT(self.code, ord('m'), 100, self) == False:
                exit()

        # 틱 데이터
        if self.ticktp == 'T':
            if self.objChart.RequestMTT(self.code, ord('T'), 100, self) == False:
                exit()

        self.stkDataHist    = CpData.StkDataHist()
        self.stkDataHist.ymd = self.dates
        self.stkDataHist.item = self.item
        
        for i in range(len(self.dates)):
            self.stkDataHist.item_nm.append(self.item_nm)
        
        self.stkDataHist.open = self.opens
        self.stkDataHist.high = self.highs
        self.stkDataHist.low = self.lows
        self.stkDataHist.close = self.closes
        self.stkDataHist.acc_vol =  self.vols
        self.stkDataHist.diff = self.diff
        
        print("def btchart1_clicked(self) ", self.code, self.item_nm, len(self.dates))
        
        self.cpdb = CpDB.CpDB()
        self.con = self.cpdb.connect()
        self.cpdb.stkhistprc(self.con, 'I', self.stkDataHist)

        #####################################################################
        # 호가 데이터 TCP 통신
        """
        for i in range(len(self.dates)):
            send_list = [ self.stkDataHist.item[i], 
                          self.stkDataHist.open[i],
                          self.stkDataHist.ymd[i],
                          self.stkDataHist.high[i], 
                          self.stkDataHist.close[i] ] 
            req_data = {
                gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
                gd.KEY_NM_DATA: send_list
            }
            
            #self.objTcpClient.tcpClient(req_data)
            
            self.ord_sock.send_pckt(req_data)
            
            time.sleep(3)
            
            #data = self.ord_sock.recv_pckt()
            #print(data.decode())
        """

    # 개수(일간) 으로 받기
    def btchart2_clicked(self):
        if self.objChart.RequestDWM(self.code, ord('D'), 100, self) == False:
            exit()
 
    # 분차트 받기
    def btchart3_clicked(self):
        if self.objChart.RequestMTT(self.code, ord('m'), 100, self) == False:
            exit()
 
        # if self.objChart.RequestMT(self.code, ord('m'), 10000, self) == False:
        #     exit()

    # 틱차트 받기
    def btchart4_clicked(self):
        if self.objChart.RequestMTT(self.code, ord('T'), 100, self) == False:
            exit()

        # if self.objChart.RequestMT(self.code, ord('T'), 500, self) == False:
        #     exit()
 
    # 주간차트
    def btchart5_clicked(self):
        if self.objChart.RequestDWM(self.code, ord('W'), 100, self) == False:
            exit()
 
    # 월간차트
    def btchart6_clicked(self):
        if self.objChart.RequestDWM(self.code, ord('M'), 100, self) == False:
            exit()
 
 
    def btchart7_clicked(self):
        charfile = 'chart.xlsx'
        
        print("btchart7_clicked")
        
        print(self.dates, len(self.dates))
        
        for i in range(len(self.dates)):
            print(self.dates[i])
        
        if (len(self.times) == 0):
            chartData = {'일자' : self.dates,
                         '시가' : self.opens,
                         '고가' : self.highs,
                         '저가' : self.lows,
                         '종가' : self.closes,
                         '거래량' : self.vols,
                         '전일대비' : self.diff,
                         '부호' : self.sign,
                        }
            df =pd.DataFrame(chartData, columns=['일자','시가','고가','저가','종가','거래량','전일대비','부호'])
        else:
            chartData = {'일자' : self.dates,
                       '시간' : self.times,
                       '시가' : self.opens,
                       '고가' : self.highs,
                       '저가' : self.lows,
                       '종가' : self.closes,
                       '전일대비' : self.diff,
                       '거래량' : self.vols,
                       '부호' : self.sign,
                       }
            df=pd.DataFrame(chartData, columns=['일자','시간','시가','고가','저가','종가','거래량','전일대비','부호'])
 
        df = df.set_index('일자')
 
        # create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(charfile, engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='Sheet1')
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
        os.startfile(charfile)
        return

    def tickEditChanged(self):
        self.ticktp = self.tickEdit.text()
        print("def tickEditChanged(self)", self.ticktp)

    def fromdtEditChanged(self):
        self.fromdt = self.fromdtEdit.text()
        print("def fromdtEditChanged(self)", self.fromdt)

    def todtEditChanged(self):
        self.todt= self.todtEdit.text()

    def codeEditChanged(self):
        code = self.codeEdit.text()
        self.setCode(code)
        print("codeEditChanged", code)
 
    def setCode(self, code):
        if len(code) < 6:
            return
 
        print(code)
        if not (code[0] == "A"):
            code = "A" + code
 
        name = com.g_objCodeMgr.CodeToName(code)
        if len(name) == 0:
            print("종목코드 확인")
            return
 
        self.label.setText(name)
        self.item_nm = name
        self.code = code
 
 
    def btnExit_clicked(self):
        exit()
 
if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("setting/logging.json", 'rt') as f:
        log_config = json.load(f)
    today = dt.today().strftime("%Y%m%d")
    log_config['handlers']['info_file_handler']['filename'] = f'../LOG/cpchart.{today}'
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("my_setting")
    logger.debug("Start")

    myWindow = CpChartWindow()
    
    signal.signal(signal.SIGINT, com.signal_handler)  # 등록
    print('Press Ctrl+C')

    myWindow.show()
    
    time.sleep(3)

    #####################################################################
    # 호가데이터 Tcp 통신
    #objThread = threading.Thread(target=myWindow.recvloop)
    #objThread.start()
    ##objThread.join()
        
    app.exec_()
 
"""
CREATE TABLE STKHISTPRC (
	YMD     VARCHAR(8) NULL DEFAULT date_format(current_timestamp(),'%Y%m%d'),
	ITEM    VARCHAR(12) NULL DEFAULT NULL,
	ITEM_NM VARCHAR(100) NULL DEFAULT NULL,
	OPEN    INT(11) NULL DEFAULT NULL,
	HIGH    INT(11) NULL DEFAULT NULL,
	LOW     INT(11) NULL DEFAULT NULL,
	CLOSE   INT(11) NULL DEFAULT NULL,
	ACC_VOL BIGINT(20) NULL DEFAULT NULL,
	DIFF    INT(11) NULL DEFAULT NULL
)
COLLATE='utf8_general_ci'
ENGINE=INNODB
;
"""