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
import creon_cpcomm  as com
import pandas as pd


###############################################################################
# 현재가와 10차 호가를 저장하기 위한 단순 저장소
class FutCurData:
    def __init__(self):
        self.ymd  = ""
        self.item = ""
        self.item_nm = ""
        self.diff = 0
        self.time = 0
        self.times = 0
        self.exp_sttl_tp = ""
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        self.amt = 0
        self.open_interest = 0
        self.fst_offer_prc = 0
        self.fst_bid_prc = 0
        self.fst_offer_vol = 0
        self.fst_bid_vol = 0
        self.acc_offer_vol = 0
        self.acc_bid_vol = 0
        self.prc_sign = 0
        self.k200_idx = 0

###############################################################################
# 현재가와 10차 호가를 저장하기 위한 단순 저장소
class FutTickData:
    def __init__(self):
        self.ask_num = [0 for _ in range(5)]  # 매도호가건수
        self.ask_qty = [0 for _ in range(5)]  # 매도호가잔량
        self.ask_prc = [0 for _ in range(5)]      # 매도호가
        self.bid_prc = [0 for _ in range(5)]      # 매수호가
        self.bid_qty = [0 for _ in range(5)]  # 매수호가잔량
        self.bid_num = [0 for _ in range(5)]  # 매수호가건수
        self.bid_tot_num = 0
        self.bid_tot_qty = 0
        self.ask_tot_num = 0
        self.ask_tot_qty = 0
        self.cur = 0  # 현재가
        self.ymd = ''
        self.item = ''
        self.item_nm = ''
        self.time = ''
        self.acc_vol = 0
        self.mkt_stat_tp = ''
        self.ask_vwap = 0
        self.bid_vwap = 0
        self.mid_vwap = 0
        self.mid_prc  = 0
        self.prc_diff = 0

class FutPricedHist:
    def __init__(self):
        self.fcode = []
        self.ymd = []
        self.time = []
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.diff = []
        self.vol = []
        self.amt = []
        self.incomp_qty = []
        self.qty = []
        self.sign = []  # 1 체결매수 2 체결매도
        self.offer1 = []
        self.bid1 = []
        self.offer_cnt1 = []
        self.bid_cnt1 = []
        self.tot_offer_cnt = []
        self.tot_bid_cnt = []

class FutChartData:
    def __init__(self):
        self.ymd     = [] 
        self.item    = [] 
        self.hhmm    = [] 
        self.tm_tp   = []
        self.open    = [] 
        self.high    = [] 
        self.low     = [] 
        self.close   = [] 
        self.acc_vol = []
                      
###############################################################################
# CpFutureMst: 선물 현재가
class CpFutureItemList:
    def __init__(self):
        pass

    def Request(self, fcodelist):
        for i in range(com.g_objFutureMgr.GetCount()):
            code = com.g_objFutureMgr.GetData(0, i)
            name = com.g_objFutureMgr.GetData(1, i)
            if (code[0] == '4'):  # spread skip
                continue
            if (code[0] == '10100'):  # 연결선물 skip
                continue

            fcodelist.append((code, name))

            print(code, name)

        return

###############################################################################
# CpFutureCurOnly : 선물 체결
class CpFutureCurOnly:
    def __init__(self):
        pythoncom.CoInitialize()
        self.name = "FutureCurOnly"  #
        self.obj = win32com.client.Dispatch("Dscbo1.FutureCurOnly")

    def Subscribe(self, code, futCurData, parent):
        # 선물코드
        self.obj.SetInputValue(0, code)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.futCurData = futCurData

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpFutureChart
class CpFutureChart:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpSysDib.FutOptChart")

    # 차트 요청 - 분간, 틱 차트
    def Request(self, code, sel_tp, term, count, start_ymd, end_ymd, hist):
        # 연결 여부 체크
        self.obj.SetInputValue(0, code)  # 종목코드
        self.obj.SetInputValue(1, ord(sel_tp))  # 1 기간별 2 개수로 받기

        if sel_tp == '1' :
            self.obj.SetInputValue(2, start_ymd)  # 2 - (ulong) 요청종료일 (기간요청인경우만입력함)
            self.obj.SetInputValue(3, end_ymd)  # 3 - (ulong) 요청시작일

        self.obj.SetInputValue(4, count)  # 조회 개수
        self.obj.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8, 9, 29])  # 요청항목 - 날짜, 시간,시가,고가,저가,종가,거래량, 거래대금, 미결제약정
        self.obj.SetInputValue(6, ord(term))  # '차트 주기 - 분/틱 'D'	일 'W'	주 'M'	월 'm'	분 'S'	초 'T'	틱
        self.obj.SetInputValue(7, 1)  # 분틱차트 주기
        self.obj.SetInputValue(8, ord('0'))  # 갭보정
        self.obj.SetInputValue(9, ord('1'))  # 수정주가 사용
        self.obj.BlockRequest()

        rqStatus = self.obj.GetDibStatus()
        rqRet = self.obj.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()

        len = self.obj.GetHeaderValue(3)

        for i in range(len):
            hist.ymd.insert(0, self.obj.GetDataValue(0, i))     # 날짜
            hist.time.insert(0, self.obj.GetDataValue(1, i))    # 시간
            hist.open.insert(0, self.obj.GetDataValue(2, i))    # 시가
            hist.high.insert(0, self.obj.GetDataValue(3, i))    # 고가
            hist.low.insert(0, self.obj.GetDataValue(4, i))     # 저가
            hist.close.insert(0, self.obj.GetDataValue(5, i))   # 종가
            hist.vol.insert(0, self.obj.GetDataValue(6, i))     # 거래량
            hist.amt.insert(0, self.obj.GetDataValue(7, i))     # 거래대금
            hist.incomp_qty.insert(0, self.obj.GetDataValue(8, i))  # 미결제약정

        return

###############################################################################
# CpFutureMst: 선물 현재가
class CpFutureMst:
    def __init__(self):
        self.obj = win32com.client.Dispatch("Dscbo1.FutureMst")

    def Request(self, code, fprice):
        self.obj.SetInputValue(0, code)
        self.obj.BlockRequest()

        rqStatus = self.obj.GetDibStatus()
        rqRet = self.obj.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        # 수신 받은 현재가 정보를 rtMst 에 저장
        fprice.cur = self.obj.GetHeaderValue(71)  # 종가

        # 5차호가
        # 37 38 39 40 41
        # 54 55 56 57 58
        for i in range(5):
            fprice.offer.append(self.obj.GetHeaderValue(37+i))  # 매도호가
            fprice.bid.append(self.obj.GetHeaderValue(54+i))  # 매수호가

        # for key, value in retItem.items():
        #     if (type(value) == float):
        #         print('%s:%.2f' % (key, value))
        #     else:
        #         print(key, ':', value)

        return True

###############################################################################
# CpSysDib.FutureJpBid : [선물 호가,호가잔량] CpSysDib.FutureJpBid
class CpSBFutureJpBid :
    def __init__(self):
        self.name = "FutureJpBid"  #
        self.obj = win32com.client.Dispatch("CpSysDib.FutureJpBid")

    def Subscribe(self, code, futTickData, parent):
        # 선물코드
        self.obj.SetInputValue(0, code)
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.futTickData = futTickData

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# CpFutureBid : 선물 시간대별 리스트 조회
class CpFutureBid:
    def __init__(self):
        self.objRq = win32com.client.Dispatch("Dscbo1.FutureBid1")

    def Request(self, code, retList):
        self.objRq.SetInputValue(0, code)
        self.objRq.SetInputValue(1, 75)  # 요청개수

        datacnt = 0
        while True:
            self.objRq.BlockRequest()

            rqStatus = self.objRq.GetDibStatus()
            rqRet = self.objRq.GetDibMsg1()
            if rqStatus != 0:
                print("통신상태", rqStatus, rqRet)
                return False

            cnt = self.objRq.GetHeaderValue(2)

            for i in range(cnt):
                item = {}
                item['시각'] = self.objRq.GetDataValue(11, i)
                item['매도호가'] = self.objRq.GetDataValue(1, i)
                item['매수호가'] = self.objRq.GetDataValue(2, i)
                item['현재가'] = self.objRq.GetDataValue(3, i)
                item['전일대비'] = self.objRq.GetDataValue(4, i)
                item['누적거래량'] = self.objRq.GetDataValue(6, i)
                item['미체결약정'] = self.objRq.GetDataValue(8, i)
                item['체결거래량'] = self.objRq.GetDataValue(9, i)

                retList.append(item)
            # end of for

            datacnt += cnt
            if self.objRq.Continue == False:
                break
            if datacnt > 500:
                break

        # end of while

        for item in retList:
            data = ''
            for key, value in item.items():
                if (type(value) == float):
                    data += '%s:%.2f' % (key, value)
                elif (type(value) == str):
                    data += '%s:%s' % (key, value)
                elif (type(value) == int):
                    data += '%s:%d' % (key, value)

                data += ' '
            print(data)
        return True


# CpFutureWeek: 선물 일자별
class CpFutureWeek:
    def __init__(self):
        self.objRq = win32com.client.Dispatch("Dscbo1.FutureWeek1")

    def Request(self, code, retList):
        self.objRq.SetInputValue(0, code)

        datacnt = 0
        while True:
            self.objRq.BlockRequest()

            rqStatus = self.objRq.GetDibStatus()
            rqRet = self.objRq.GetDibMsg1()
            if rqStatus != 0:
                print("통신상태", rqStatus, rqRet)
                return False

            cnt = self.objRq.GetHeaderValue(0)

            for i in range(cnt):
                item = {}
                item['일자'] = self.objRq.GetDataValue(0, i)
                item['시가'] = self.objRq.GetDataValue(1, i)
                item['고가'] = self.objRq.GetDataValue(2, i)
                item['저가'] = self.objRq.GetDataValue(3, i)
                item['종가'] = self.objRq.GetDataValue(4, i)
                item['전일대비'] = self.objRq.GetDataValue(5, i)
                item['누적거래량'] = self.objRq.GetDataValue(6, i)
                item['거래대금'] = self.objRq.GetDataValue(7, i)
                item['미결제약정'] = self.objRq.GetDataValue(8, i)

                retList.append(item)
            # end of for

            datacnt += cnt
            if self.objRq.Continue == False:
                break
        # end of while

        for item in retList:
            data = ''
            for key, value in item.items():
                if (type(value) == float):
                    data += '%s:%.2f' % (key, value)
                elif (type(value) == str):
                    data += '%s:%s' % (key, value)
                elif (type(value) == int):
                    data += '%s:%d' % (key, value)

                data += ' '
            print(data)
        return True
