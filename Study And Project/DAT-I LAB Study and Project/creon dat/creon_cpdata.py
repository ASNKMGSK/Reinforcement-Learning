import sys
from PyQt5.QtWidgets import *
import win32com.client
from enum import Enum
from time import sleep
import threading
import pythoncom
import time
import asyncio

import creon_cpevent as CpEvent
import pandas as pd
import creon_cpcomm     as com

###############################################################################
# 과거데이터 저장
class StkDataHist:
    def __init__(self):
        self.item = []
        self.item_nm = []
        self.ymd = []
        self.time = []
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.diff = []
        self.acc_vol = []
        self.vol = []
        self.amt = []
        self.incomp_qty = []
        self.qty = []
        self.sign = []  # 1 체결매수 2 체결매도
        self.offer1 = []
        self.bid1 = []
        self.offer_cnt1 = []
        self.bid_qty1 = []
        self.tot_offer_cnt = []
        self.tot_bid_qty = []
        self.stk_tp = []
        self.base_item = []
        self.base_item_nm = []
        
###############################################################################
# 투자자별 매매동향
class InvestData:
    def __init__(self):
        self.tp     = []      # 투자자
        self.time   = []      #
        self.kospi  = []      #
        self.kosdaq = []
        self.future = []

class Ivt7222:
    def __init__(self):
        self.mkt_tp = []
        self.mkt_nm = []
        self.ivt_tp       = []
        self.ivt_nm       = []
        self.time         = []
        self.ask_qty      = []
        self.ask_amt      = []
        self.bid_qty      = []
        self.bid_amt      = []
        self.net_bid_qty  = []
        self.net_bid_amt  = []

###############################################################################
# 현재가와 10차 호가를 저장하기 위한 단순 저장소
class StkCurData:
    def __init__(self):
        self.ymd  = ""
        self.item = ""
        self.item_nm = ""
        self.diff = 0
        self.time = 0
        self.times = 0
        self.exp_con_tp = ""
        self.open = 0
        self.high = 0
        self.low = 0
        self.bf_close = 0
        self.close = 0
        self.short_prc = 0
        self.long_prc = 0
        self.vol = 0
        self.acc_vol = 0
        self.amt = 0
        self.odr_tp = 0
        self.cur = 0
        self.prc_sign = 0
        self.acc_short_qty = 0  # 15 - (long) 누적매도체결수량 (체결가방식)
        self.acc_long_qty = 0 # 16 - (long) 누적매수체결수량 (체결가방식)
        self.acc_short_ack_qty = 0  # 27 - (long) 누적매도체결수량 (호가방식)
        self.acc_long_ack_qty = 0  # 28 - (long) 누적매수체결수량 (호가방식)

###############################################################################
# 현재가와 10차 호가를 저장하기 위한 단순 저장소
class StkTickData:
    def __init__(self):
        self.ymd = ''
        self.item = ''
        self.item_nm = ''
        self.time = 0
        self.acc_vol = 0
        self.ask_vwap = 0
        self.bid_vwap = 0
        self.mid_vwap = 0
        self.mid_prc  = 0
        self.prc_diff = 0
        self.cur = 0            # 현재가
        self.baseprice = 0      # 기준가
        self.ask_prc = [0 for _ in range(10)]       # 매도호가
        self.bid_prc = [0 for _ in range(10)]       # 매수호가
        self.ask_qty = [0 for _ in range(10)]       # 매도잔량
        self.bid_qty = [0 for _ in range(10)]       # 매수잔량
        self.ask_num = [0 for _ in range(10)]      # 매도대비
        self.bid_num = [0 for _ in range(10)]      # 매수대비
        self.ask_tot_qty = 0
        self.bid_tot_qty = 0
        self.extime_ask_tot_qty = 0
        self.extime_bid_tot_qty = 0
        self.acc_vol = 0

###############################################################################
# plus 실시간 수신 base 클래스
class CpPublish:
    def __init__(self, name, serviceID):
        self.name = name
        self.obj = win32com.client.Dispatch(serviceID)
        self.bIsSB = False

    def Subscribe(self, var, caller):
        if self.bIsSB:
            self.Unsubscribe()

        if (len(var) > 0):
            self.obj.SetInputValue(0, var)

        handler = win32com.client.WithEvents(self.obj, CpEvent)
        handler.set_params(self.obj, self.name, caller)
        self.obj.Subscribe()
        self.bIsSB = True

    def Unsubscribe(self):
        if self.bIsSB:
            self.obj.Unsubscribe()
        self.bIsSB = False

###############################################################################
# CpPBStockCur: 실시간 현재가 요청 클래스
class CpPBStockCur(CpPublish):
    def __init__(self):
        super().__init__('stockcur', 'DsCbo1.StockCur')

###############################################################################
# 투자자별
class Cp7222:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpSysDib.CpSvrNew7222")
        self.InputIdx = {
            'B': '거래소',
            'C': '코스닥',
            'D': '선  물',
            'E': '콜옵션',
            'F': '풋옵션'
        }
        self.InvestIdx = {
            1: '개  인',
            2: '외국인',
            3: '기관계'
        }

    # 시장전체
    def Request(self, caller):

        caller.mkt_tp = []
        caller.mkt_nm = []
        caller.ivt_tp = []
        caller.ivt_nm = []
        caller.time = []
        caller.ask_qty = []
        caller.ask_amt = []
        caller.bid_qty = []
        caller.bid_amt = []
        caller.net_bid_qty = []
        caller.net_bid_amt = []

        # 시장구분
        i = 0
        for key, value in self.InputIdx.items():
            # 투자자
            for investkey, investvalue in self.InvestIdx.items():

                self.obj.SetInputValue(0, ord(key))  #
                self.obj.SetInputValue(1, investkey)  # 투자자구분
                self.obj.SetInputValue(2, ord('1'))  # 누적
                #self.obj.SetInputValue(3, 847)  # 요청시간
                self.obj.SetInputValue(4, ord('1'))  # 계약, 금액

                self.obj.BlockRequest()

                # 통신 및 통신 에러 처리
                rqStatus = self.obj.GetDibStatus()
                print("통신상태", rqStatus, self.obj.GetDibMsg1())
                if rqStatus != 0:
                    return False

                print("key, value ====================================")
                print("key, value ", key, value, investkey, investvalue)
                cnt = self.obj.GetHeaderValue(0)

                if cnt != 0:
                    caller.mkt_tp.append(key)
                    caller.mkt_nm.append(value)
                    caller.ivt_tp.append(investkey)
                    caller.ivt_nm.append(investvalue)
                    caller.time.append(self.obj.GetDataValue(0, investkey))
                    caller.ask_qty.append(self.obj.GetDataValue(1, investkey))
                    caller.ask_amt.append(self.obj.GetDataValue(2, investkey))
                    caller.bid_qty.append(self.obj.GetDataValue(3, investkey))
                    caller.bid_amt.append(self.obj.GetDataValue(4, investkey))
                    caller.net_bid_qty.append(self.obj.GetDataValue(5, investkey))
                    caller.net_bid_amt.append(self.obj.GetDataValue(6, investkey))

                    print(caller.mkt_tp[i], caller.mkt_nm[i], caller.ivt_tp[i], caller.ivt_nm[i], caller.time[i], caller.ask_qty[i], caller.ask_amt[i])
                    i = i+1

                print("key, value end ====================================")

        return
###############################################################################
# CpStockChart
# self.obj.SetInputValue(6, ord(term))  # '차트 주기 - 일간 차트 요청 D W M m : 분 T 틱
class CpStockChart:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpSysDib.StockChart")

    # 차트 요청 - 기간 기준으로
    #def Request(self, item, sel_tp, term, count, start_ymd, end_ymd, hist):
    def Request(self, item, sel_tp, term, count, start_ymd, end_ymd, stkDataHist):

        self.obj.SetInputValue(0, item)  # 종목코드
        self.obj.SetInputValue(1, ord(sel_tp))  # sel_tp : 1 기간, 2 개수
        self.obj.SetInputValue(3, start_ymd)  # From 날짜
        self.obj.SetInputValue(2, end_ymd)  # To 날짜
        self.obj.SetInputValue(4, count)  # 최근 500일치
        self.obj.SetInputValue(5, [0, 1, 2, 3, 4, 5, 6, 8, 37])  # 날짜,시간, 시가,고가,저가,종가,전일대비, 거래량, 부호
        self.obj.SetInputValue(6, ord(term))  # '차트 주기 - 일간 차트 요청 M m
        self.obj.SetInputValue(9, ord('1'))  # 수정주가 사용
        #self.obj.BlockRequest()

        #####################################################################
        # 기간
        if  sel_tp == '1':
            sumCnt = 0
            chk_ymd = start_ymd
            while(int(chk_ymd) <= int(end_ymd)):
                self.obj.BlockRequest()

                rqStatus = self.obj.GetDibStatus()
                rqRet = self.obj.GetDibMsg1()
                print("통신상태", rqStatus, rqRet)
                if rqStatus != 0:
                    exit()

                cnt = self.obj.GetHeaderValue(3)
                lstCnt = self.obj.GetHeaderValue(4) # 마지막봉틱수
                for i in range(cnt):
                    stkDataHist.item.insert(0, item)  # 날짜
                    stkDataHist.ymd.insert(0, self.obj.GetDataValue(0, i))  # 날짜
                    stkDataHist.time.insert(0, self.obj.GetDataValue(1, i))  # 시간
                    stkDataHist.open.insert(0, self.obj.GetDataValue(2, i))  # 시가
                    stkDataHist.high.insert(0, self.obj.GetDataValue(3, i))  # 고가
                    stkDataHist.low.insert(0, self.obj.GetDataValue(4, i))  # 저가
                    stkDataHist.close.insert(0, self.obj.GetDataValue(5, i))  # 종가
                    stkDataHist.diff.insert(0, self.obj.GetDataValue(6, i))  # 전일대비
                    stkDataHist.vol.insert(0, self.obj.GetDataValue(7, i))  # 거래량

                    chk_ymd = self.obj.GetDataValue(0, i)

                sumCnt  = sumCnt + cnt

                print(" while(stkDataHist.ymd.last <= end_ymd): ", stkDataHist.ymd[0], cnt, lstCnt)
        #####################################################################
        # 개수
        elif sel_tp == '2':
            sumCnt = 0
            while (sumCnt <= count):
                self.obj.BlockRequest()

                rqStatus = self.obj.GetDibStatus()
                rqRet = self.obj.GetDibMsg1()
                print("통신상태", rqStatus, rqRet)
                if rqStatus != 0:
                    exit()

                cnt = self.obj.GetHeaderValue(3)
                lstCnt = self.obj.GetHeaderValue(4)  # 마지막봉틱수
                for i in range(cnt):
                    stkDataHist.item.insert(0, item)  # 날짜
                    stkDataHist.ymd.insert(0, self.obj.GetDataValue(0, i))  # 날짜
                    stkDataHist.time.insert(0, self.obj.GetDataValue(1, i))  # 시간
                    stkDataHist.open.insert(0, self.obj.GetDataValue(2, i))  # 시가
                    stkDataHist.high.insert(0, self.obj.GetDataValue(3, i))  # 고가
                    stkDataHist.low.insert(0, self.obj.GetDataValue(4, i))  # 저가
                    stkDataHist.close.insert(0, self.obj.GetDataValue(5, i))  # 종가
                    stkDataHist.diff.insert(0, self.obj.GetDataValue(6, i))  # 전일대비
                    stkDataHist.vol.insert(0, self.obj.GetDataValue(7, i))  # 거래량

                sumCnt = sumCnt + cnt

                print("while (sumCnt <= count): ", stkDataHist.ymd[sumCnt-1], cnt, lstCnt)
        else:
            return
        # for i in range(0, len, 1):
        #     if i < 100 :
        #         print("i > ", len, i, stkDataHist.ymd[i], stkDataHist.time[i], stkDataHist.open[i])

        # reverse
        # for i in range(len-1, -1, -1):
        #     print("i > ", len, i, stkDataHist.ymd[i], stkDataHist.time[i], stkDataHist.open[i])

        return

"""
        df1 = pd.DataFrame(data, columns=['date', 'times', 'closes'])
        print(df1)
        print(len)

        ma5 = df1['closes'].rolling(window=5).mean()
        ma10 = df1['closes'].rolling(window=10).mean()
        ma20 = df1['closes'].rolling(window=20).mean()
        ma60 = df1['closes'].rolling(window=60).mean()
        ma120 = df1['closes'].rolling(window=120).mean()

        data_ma = {"ma5": ma5,
                   "ma10": ma10,
                   "ma20": ma20,
                   }

        print(data_ma)

        df_ma = pd.DataFrame(data_ma, columns=['ma5', 'ma10', 'ma20'])

        print(df_ma)

        # 가격 비교
        # 매수
        # 체결내역확인
        # 잔고확인
"""


###############################################################################
# CpInvestor: 실시간 현재가 요청 클래스
class CpInvestor:
    def __init__(self):
        self.name = "rpinvestor"
        self.obj = win32com.client.Dispatch("CpSysDib.CpSvrNew7221")
        self.InvestIndex = {
            0: '거래소주식',
            1: '코스닥주식',
            2: '선물',
            3: '옵션콜',
            4: '옵션풋',
            5: '주식콜',
            6: '주식풋',
            7: '스타지수선물',
            8: '주식선물',
            9: '채권선물 3년국채(오픈예정)',
            10: '채권선물 5년국채(오픈예정)',
            11: '채권선물 10년국체(오픈예정)',
            12: '금리선물 CD(오픈예정)',
            13: '금리선물통안증권(오픈예정)',
            14: '통화선물미국달러(오픈예정)',
            15: '통화선물엔(오픈예정)',
            16: '통화선물유로(오픈예정)',
            17: '금속상품선물금(오픈예정)',
            18: '농산물파생선물돈육(오픈예정)',
            19: '통화콜옵션미국달러(오픈예정)',
            20: '통화풋옵션미국달러(오픈예정)',
            21: 'CME선물',
            22: '미니금선물'
        }

    def Request(self):
        self.obj.SetInputValue(0, ord('1'))  # 옵션금액 선물계약
        self.obj.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = self.obj.GetDibStatus()
        print("통신상태", rqStatus, self.obj.GetDibMsg1())
        if rqStatus != 0:
            return False

        time = self.obj.GetHeaderValue(0)
        cnt =  self.obj.GetHeaderValue(1)

        print("시간 " , time, cnt)

        for key, value in self.InvestIndex.items():
            dicInvest = {}
            dicInvest['개인매도'] = self.obj.GetDataValue(0, key)
            dicInvest['개인매수'] = self.obj.GetDataValue(1, key)
            dicInvest['개인순매수'] = self.obj.GetDataValue(2, key)
            dicInvest['외국인매도'] = self.obj.GetDataValue(3, key)
            dicInvest['외국인매수'] = self.obj.GetDataValue(4, key)
            dicInvest['외국인순매수'] = self.obj.GetDataValue(5, key)
            dicInvest['기관매도'] = self.obj.GetDataValue(6, key)
            dicInvest['기관매수'] = self.obj.GetDataValue(7, key)
            dicInvest['기관순매수'] = self.obj.GetDataValue(8, key)

            print(value)
            print(dicInvest)

###############################################################################
# CpPBInvestor: 실시간 현재가 요청 클래스
class CpSBInvestor:
    def __init__(self):
        self.name = "pbinvestor"
        self.obj = win32com.client.Dispatch("CpSysDib.CpSvrNew7221S")
        self.InvestIndex = {
            0: '거래소주식',
            1: '코스닥주식',
            2: '선물',
            3: '옵션콜',
            4: '옵션풋',
            5: '주식콜',
            6: '주식풋',
            7: '스타지수선물',
            8: '주식선물',
            9: '채권선물 3년국채(오픈예정)',
            10: '채권선물 5년국채(오픈예정)',
            11: '채권선물 10년국체(오픈예정)',
            12: '금리선물 CD(오픈예정)',
            13: '금리선물통안증권(오픈예정)',
            14: '통화선물미국달러(오픈예정)',
            15: '통화선물엔(오픈예정)',
            16: '통화선물유로(오픈예정)',
            17: '금속상품선물금(오픈예정)',
            18: '농산물파생선물돈육(오픈예정)',
            19: '통화콜옵션미국달러(오픈예정)',
            20: '통화풋옵션미국달러(오픈예정)',
            21: 'CME선물',
            22: '미니금선물'
        }

    def Subscribe(self, item, parent):
        self.obj.SetInputValue(0, item)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpSBStockCur: 실시간 현재가 요청 클래스
class CpSBStockCur:
    def __init__(self):
        pythoncom.CoInitialize()
        self.name = "stockcur"
        self.obj = win32com.client.Dispatch("DsCbo1.StockCur")

    def Subscribe(self, item, stkCurData, parent):
        self.obj.SetInputValue(0, item)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.stkCurData = stkCurData

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpSBStockBid: 실시간 10차 호가 요청 클래스
class CpSBStockBid:
    def __init__(self):
        pythoncom.CoInitialize()
        self.name = "stockbid" #stockjpbid
        self.obj = win32com.client.Dispatch("Dscbo1.StockJpBid")
 
    def Subscribe(self, item, stkTickData, parent):
        self.obj.SetInputValue(0, item)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.stkTickData = stkTickData
 
            
    def Unsubscribe(self):
        self.obj.Unsubscribe()


###############################################################################
# CpSBStockBid: 실시간 10차 호가 요청 클래스
class CpSBStockJpBid2:
    def __init__(self):
        # pythoncom.CoInitializeEx(0)

        self.name = "stockbid2"  # stockjpbid
        self.obj = win32com.client.Dispatch("Dscbo1.StockJpBid2")

    def Subscribe(self, item, stkTickData, parent):
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.stkTickData = stkTickData
        self.obj.SetInputValue(0, item)

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpSBStockBid: 실시간 10차 호가 요청 클래스
class CpSBStockIndexIS:
    def __init__(self):
        # pythoncom.CoInitialize()
        self.name = "stockindexis"
        self.obj = win32com.client.Dispatch("Dscbo1.StockIndexIS")

    def Subscribe(self, item, stkCurData, parent):
        self.obj.SetInputValue(0, item)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.stkCurData = stkCurData

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpCurrentPrice : 주식 현재가 및 10차 호가 조회
class CpSBStockCurBid:
    def __init__(self):
        self.name = "CpSBStockCurBid"  # stockjpbid

    def Subscribe(self, obj, item, stkTickData, parent):
        handler = win32com.client.WithEvents(obj, CpEvent.CpEvent)
        handler.set_params(obj, self.name, parent)
        obj.SetInputValue(0, item)
        self.stkTickData = stkTickData
        obj.Request()
        com.MessagePump(10000)

        # 수신 받은 현재가 정보를 rtMst 에 저장
        stkTickData.cur = obj.GetHeaderValue(11)  # 종가
        print("stkTickData.cur > ", stkTickData.cur)

        return

###############################################################################
# CpCurrentPrice : 주식 현재가 및 10차 호가 조회
class CpStockCurBid:
    def __init__(self):
        pass

    def Request(self, item, stkTickData):
        # 현재가 통신
        print("class CpStockCurBid:")

        pythoncom.CoInitialize()
        self.objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")
        self.objStockjpbid2 = win32com.client.Dispatch("DsCbo1.StockJpBid2")

        self.objStockMst.SetInputValue(0, item)
        self.objStockMst.BlockRequest()

        print("통신상태", self.objStockMst.GetDibStatus(), self.objStockMst.GetDibMsg1())
        if self.objStockMst.GetDibStatus() != 0:
            return False

        # 수신 받은 현재가 정보를 rtMst 에 저장
        stkTickData.cur = self.objStockMst.GetHeaderValue(11)  # 종가
        print("stkTickData.cur > ", stkTickData.cur)

        # 10차 호가 통신
        self.objStockjpbid2.SetInputValue(0, item)
        self.objStockjpbid2.BlockRequest()

        print("통신상태", self.objStockjpbid2.GetDibStatus(), self.objStockjpbid2.GetDibMsg1())
        if self.objStockjpbid2.GetDibStatus() != 0:
            return False

        # 10차호가
        for i in range(10):
            stkTickData.ask_prc.append(self.objStockjpbid2.GetDataValue(0, i))  # 매도호가
            stkTickData.bid_prc.append(self.objStockjpbid2.GetDataValue(1, i))    # 매수호가
            stkTickData.ask_qty.append(self.objStockjpbid2.GetDataValue(2, i))   # 매도잔량
            stkTickData.bid_qty.append(self.objStockjpbid2.GetDataValue(3, i))   # 매수잔량
            stkTickData.ask_num.append(self.objStockjpbid2.GetDataValue(4, i)) # 매도잔량대비
            stkTickData.bid_num.append(self.objStockjpbid2.GetDataValue(5, i)) # 매수잔량대비

            print(i + 1, "차 매도/매수 호가 Request : ", stkTickData.ask_prc[i], stkTickData.bid_prc[i])

        #for debug
        for i in range(10):
           print(i+1, "차 매도/매수 호가 Request : ", stkTickData.ask_prc[i], stkTickData.bid_prc[i])
        
        return True


###############################################################################
# CpCurrentPrice : 주식 현재가 및 10차 호가 조회
class CpStockCurBid2:
    def __init__(self):
        pass
        # self.objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        # bConnect = self.objCpCybos.IsConnect
        # if (bConnect == 0):
        #     print("PLUS가 정상적으로 연결되지 않음. ")
        #     return

    def Request(self, objStockMst, item, stkTickData):
        # 현재가 통신
        print("class CpStockCurBid:")

        pythoncom.CoInitialize()

        objStockMst.SetInputValue(0, item)
        objStockMst.BlockRequest()

        # print("통신상태", self.objStockMst.GetDibStatus(), self.objStockMst.GetDibMsg1())
        # if self.objStockMst.GetDibStatus() != 0:
        #     return False

        # 수신 받은 현재가 정보를 rtMst 에 저장
        stkTickData.cur = objStockMst.GetHeaderValue(11)  # 종가
        print("stkTickData.cur > ", stkTickData.cur)

        # # 10차 호가 통신
        # self.objStockjpbid2.SetInputValue(0, item)
        # self.objStockjpbid2.BlockRequest()
        #
        # print("통신상태", self.objStockjpbid2.GetDibStatus(), self.objStockjpbid2.GetDibMsg1())
        # if self.objStockjpbid2.GetDibStatus() != 0:
        #     return False
        #
        # # 10차호가
        # for i in range(10):
        #     stkTickData.offer.append(self.objStockjpbid2.GetDataValue(0, i))  # 매도호가
        #     stkTickData.bid.append(self.objStockjpbid2.GetDataValue(1, i))    # 매수호가
        #     stkTickData.ask_qty.append(self.objStockjpbid2.GetDataValue(2, i))   # 매도잔량
        #     stkTickData.bid_qty.append(self.objStockjpbid2.GetDataValue(3, i))   # 매수잔량
        #     stkTickData.offer_diff.append(self.objStockjpbid2.GetDataValue(4, i)) # 매도잔량대비
        #     stkTickData.bid_diff.append(self.objStockjpbid2.GetDataValue(5, i)) # 매수잔량대비
        #
        #     print(i + 1, "차 매도/매수 호가 Request : ", stkTickData.offer[i], stkTickData.bid[i])

        # for debug
        # for i in range(10):
        #    print(i+1, "차 매도/매수 호가 Request : ", rtMst.offer[i], rtMst.bid[i])

        return True
###############################################################################
#   주식 Request
class CpStockMst:
    def Request(self, item):
        # 현재가 객체 구하기
        objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")
        objStockMst.SetInputValue(0, item)  # 종목 코드 - 삼성전자
        objStockMst.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = objStockMst.GetDibStatus()
        rqRet = objStockMst.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        # 현재가 정보 조회
        item = objStockMst.GetHeaderValue(0)  # 종목코드
        name = objStockMst.GetHeaderValue(1)  # 종목명
        time = objStockMst.GetHeaderValue(4)  # 시간
        cprice = objStockMst.GetHeaderValue(11)  # 종가
        diff = objStockMst.GetHeaderValue(12)  # 대비
        open = objStockMst.GetHeaderValue(13)  # 시가
        high = objStockMst.GetHeaderValue(14)  # 고가
        low = objStockMst.GetHeaderValue(15)  # 저가
        offer = objStockMst.GetHeaderValue(16)  # 매도호가
        bid = objStockMst.GetHeaderValue(17)  # 매수호가
        vol = objStockMst.GetHeaderValue(18)  # 거래량
        vol_value = objStockMst.GetHeaderValue(19)  # 거래대금

        print("코드 이름 시간 현재가 대비 시가 고가 저가 매도호가 매수호가 거래량 거래대금")
        print(item, name, time, cprice, diff, open, high, low, offer, bid, vol, vol_value)
        return True


################################################
# CpMarketEye : 복수종목 현재가 통신 서비스
class CpMarketEye:
    def __init__(self):
        # 요청 필드 배열 - 종목코드, 시간, 대비부호 대비, 현재가, 거래량, 종목명
        self.rqField = [0, 1, 2, 3, 4, 10, 17]  # 요청 필드

        # 관심종목 객체 구하기
        pythoncom.CoInitialize()
        self.obj = win32com.client.Dispatch("CpSysDib.MarketEye")

    def Request(self, items, stkCurData):
        # 요청 필드 세팅 - 종목코드, 종목명, 시간, 대비부호, 대비, 현재가, 거래량
        self.obj.SetInputValue(0, self.rqField)  # 요청 필드
        self.obj.SetInputValue(1, items)  # 종목코드 or 종목코드 리스트
        self.obj.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = self.obj.GetDibStatus()
        rqRet = self.obj.GetDibMsg1()

        print("통신상태", rqStatus, rqRet, items)

        if rqStatus != 0:
            return False

        cnt = self.obj.GetHeaderValue(2)

        for i in range(cnt):
            stkCurData.ymd      = com.dtymd
            stkCurData.item     = self.obj.GetDataValue(0, i)  # 코드
            stkCurData.item_nm  = com.g_objCodeMgr.CodeToName(stkCurData.item)

            stkCurData.diff     = self.obj.GetDataValue(3, i)
            stkCurData.close    = self.obj.GetDataValue(4, i)
            stkCurData.acc_vol  = self.obj.GetDataValue(5, i)  # 거래량

            # item['item'] =
            # # rpName = self.objRq.GetDataValue(1, i)  # 종목명
            # # rpDiffFlag = self.objRq.GetDataValue(3, i)  # 대비부호
            # item['diff'] = self.obj.GetDataValue(3, i)  # 대비
            # item['cur'] = self.obj.GetDataValue(4, i)  # 현재가
            # item['vol'] = self.obj.GetDataValue(5, i)  # 거래량
            #
            # caller.curDatas[item['item']] = item

        return True


################################################
# CpMarketEye : 복수종목 현재가 통신 서비스
class CpMarketEye2:
    def __init__(self):
        # 관심종목 객체 구하기
        # pythoncom.CoInitialize()
        # self.obj = win32com.client.Dispatch("CpSysDib.MarketEye")
        pass

    def Request(self, obj, items, stkCurData):

        # 요청 필드 배열 - 종목코드, 시간, 대비부호 대비, 현재가, 거래량, 종목명
        self.rqField = [0, 1, 2, 3, 4, 10, 17]  # 요청 필드

        # 요청 필드 세팅 - 종목코드, 종목명, 시간, 대비부호, 대비, 현재가, 거래량
        obj.SetInputValue(0, self.rqField)  # 요청 필드
        obj.SetInputValue(1, items)  # 종목코드 or 종목코드 리스트
        obj.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = obj.GetDibStatus()
        rqRet    = obj.GetDibMsg1()

        print("통신상태", rqStatus, rqRet, items)

        if rqStatus != 0:
            return False

        cnt = obj.GetHeaderValue(2)

        for i in range(cnt):
            stkCurData.ymd      = com.dtymd
            stkCurData.item     = obj.GetDataValue(0, i)  # 코드
            stkCurData.item_nm  = com.g_objCodeMgr.CodeToName(stkCurData.item)

            stkCurData.diff     = obj.GetDataValue(3, i)
            stkCurData.close    = obj.GetDataValue(4, i)
            stkCurData.acc_vol  = obj.GetDataValue(5, i)  # 거래량

            # item['item'] =
            # # rpName = self.objRq.GetDataValue(1, i)  # 종목명
            # # rpDiffFlag = self.objRq.GetDataValue(3, i)  # 대비부호
            # item['diff'] = self.obj.GetDataValue(3, i)  # 대비
            # item['cur'] = self.obj.GetDataValue(4, i)  # 현재가
            # item['vol'] = self.obj.GetDataValue(5, i)  # 거래량
            #
            # caller.curDatas[item['item']] = item

        return True