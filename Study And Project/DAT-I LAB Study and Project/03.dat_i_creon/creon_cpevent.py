import sys
from PyQt5.QtWidgets import *
import win32com.client
from enum import Enum
from time import sleep
import threading
import pythoncom
import time
import asyncio

import creon_cpcomm as com

import win32event
StopEvent = win32event.CreateEvent(None, 0, 0, None)

###############################################################################
# CpEvent: 실시간 이벤트 수신 클래스
class CpEvent:
    def set_params(self, client, name, parent):
        self.client = client  # CP 실시간 통신 object
        self.name = name  # 서비스가 다른 이벤트를 구분하기 위한 이름
        self.parent = parent  # callback 을 위해 보관

        # 데이터 변환용
        self.concdic = {"1": "체결", "2": "확인", "3": "거부", "4": "접수"}
        self.buyselldic = {"1": "매도", "2": "매수"}
        print(self.concdic)
        print(self.buyselldic)

    # PLUS 로 부터 실제로 시세를 수신 받는 이벤트 핸들러
    def OnReceived(self):

        print("===================================================")
        print("def OnReceived(self)", self.name)
        print("===================================================")

        if self.name == "stockcur":
            # 현재가 체결 데이터 실시간 업데이트

            self.parent.stkCurData.ymd = com.dtymd
            self.parent.stkCurData.item = self.client.GetHeaderValue(0)  # 0 - (string) 종목코드
            self.parent.stkCurData.item_nm = self.client.GetHeaderValue(1)  # 1 - (string) 종목명
            self.parent.stkCurData.diff = self.client.GetHeaderValue(2)  # 2 - (long) 전일대비
            self.parent.stkCurData.time = self.client.GetHeaderValue(3)  # 3 - (long) 시간
            self.parent.stkCurData.times = self.client.GetHeaderValue(18)  # 18 - (long) 시간 (초)
            self.parent.stkCurData.exp_con_tp = chr(self.client.GetHeaderValue(19))  # 19 - (char)예상체결가구분플래그
            self.parent.stkCurData.open = self.client.GetHeaderValue(4)  # 4 - (long) 시가
            self.parent.stkCurData.high = self.client.GetHeaderValue(5)  # 5 - (long) 고가
            self.parent.stkCurData.low = self.client.GetHeaderValue(6)  # 6 - (long) 저가
            self.parent.stkCurData.short_prc = self.client.GetHeaderValue(7)  # 7 - (long) 매도호가
            self.parent.stkCurData.long_prc = self.client.GetHeaderValue(8)  # 8 - (long) 매수호가
            self.parent.stkCurData.vol = self.client.GetHeaderValue(17)  # 17 - (long) 순간체결수량
            self.parent.stkCurData.acc_vol = self.client.GetHeaderValue(9)  # 9 - (long) 누적거래량[주의] 기준단위를확인하세요
            self.parent.stkCurData.amt = self.client.GetHeaderValue(10)  # 10 - (long) 누적거래대금[주의] 기준단위를확인하세요
            self.parent.stkCurData.odr_tp = chr(self.client.GetHeaderValue(14))  # 14 - (char)체결상태       1 매수 2 매도
            self.parent.stkCurData.cur = self.client.GetHeaderValue(13)  # 현재가
            self.parent.stkCurData.close = self.client.GetHeaderValue(13)  # 현재가

            self.parent.prc_sign = self.client.GetHeaderValue(22)  # 22 - (char)대비부호
            self.parent.acc_short_qty = self.client.GetHeaderValue(15)  # 15 - (long) 누적매도체결수량 (체결가방식)
            self.parent.acc_long_qty = self.client.GetHeaderValue(16)  # 16 - (long) 누적매수체결수량 (체결가방식)
            self.parent.acc_short_ack_qty = self.client.GetHeaderValue(27)  # 27 - (long) 누적매도체결수량 (호가방식)
            self.parent.acc_long_ack_qty = self.client.GetHeaderValue(28)  # 28 - (long) 누적매수체결수량 (호가방식)

            # # 장중이 아니면 처리 안함.
            if self.parent.stkCurData.exp_con_tp != '2':
                 return

            # 현재가 업데이트
            print("PB > 현재가 업데이트 : ", self.parent.stkCurData.ymd, self.parent.stkCurData.item, self.parent.stkCurData.item_nm, self.parent.stkCurData.cur, self.parent.stkCurData.exp_con_tp)

            # 현재가 변경  call back 함수 호출
            self.parent.monitorCurPriceChange()

            return

        elif self.name == "CpSBStockCurBid":
            print("CpSBStockCurBid")
            win32event.SetEvent(StopEvent)
            return

        elif self.name == "stockindexis":

            self.parent.stkCurData.ymd = com.dtymd
            self.parent.stkCurData.time = self.client.GetHeaderValue(1)  # 1 - (long) 시간
            self.parent.stkCurData.close = self.client.GetHeaderValue(2)  # 현재가
            self.parent.stkCurData.diff = self.client.GetHeaderValue(3)  # 2 - (float) 전일대비
            self.parent.stkCurData.acc_vol = self.client.GetHeaderValue(4)  # 9 - (long) 누적거래량[주의] 기준단위를확인하세요
            self.parent.stkCurData.amt = self.client.GetHeaderValue(5)  # 10 - (long) 누적거래대금[주의] 기준단위를확인하세요

            self.parent.stkCurData.item_nm = self.client.GetHeaderValue(6)  # 업종명
            self.parent.stkCurData.item = self.client.GetHeaderValue(7)  # 업종코드

            print(self.parent.stkCurData.ymd, self.parent.stkCurData.item, self.parent.stkCurData.time, self.parent.stkCurData.close)

            self.parent.monitorIndexChange()

            return

        elif self.name == "FutureJpBid":

            print("PB > 종목코드 선물 ", self.client.GetHeaderValue(0))

            # futuremst 버퍼 확장
            # 현재가 5차 호가 데이터 실시간 업데이트
            # 2,3,4,5,6  - (float) 매도 1 우선호가
            # 7,8,9,10,11 - (long) 매도 1 우선호가잔량
            # 13 14 15 16 17  13 - (short) 매도 1 우선호가건수
            # 19,20,21,22,23  - 매수 1 우선호가
            # 24,25,26,27,28  - (long) 매수 1우선호가잔량
            # 30 31 32 33 34  - (short) 매수 1 우선호가건수
            for i in range(5):
                self.parent.futTickData.ask_prc[i] = self.client.GetHeaderValue(2+i)
                self.parent.futTickData.ask_qty[i] = self.client.GetHeaderValue(7+i)
                self.parent.futTickData.ask_num[i] = self.client.GetHeaderValue(13 + i)
                self.parent.futTickData.bid_prc[i] = self.client.GetHeaderValue(19+i)
                self.parent.futTickData.bid_qty[i] = self.client.GetHeaderValue(24+i)
                self.parent.futTickData.bid_num[i] = self.client.GetHeaderValue(30 + i)

            self.parent.futTickData.ymd    = com.dtymd
            self.parent.futTickData.item   = self.client.GetHeaderValue(0)
            self.parent.futTickData.time   = self.client.GetHeaderValue(1)
            self.parent.futTickData.ask_tot_qty = self.client.GetHeaderValue(12) # 12 - (long) 매도총호가잔량
            self.parent.futTickData.ask_tot_num = self.client.GetHeaderValue(18) # 18 - (long) 매도총우선호가건수
            self.parent.futTickData.bid_tot_qty = self.client.GetHeaderValue(29)  # 29 - (long) 매수총호가잔량
            self.parent.futTickData.bid_tot_num = self.client.GetHeaderValue(35)  # 35 - (long) 매수총우선호가건수
            self.parent.futTickData.mkt_stat_tp = self.client.GetHeaderValue(36)  # 36 - (short) 장상태구분

            print("FutureJpBid", self.parent.futTickData.ask_num[0], self.parent.futTickData.ask_qty[0], self.parent.futTickData.ask_prc[0])

            self.parent.monitorTickChangeFut()

            return True

        elif self.name == "FutureCurOnly":

            print("PB > FutureCurOnly ", self.client.GetHeaderValue(0))
            print("PB > FutureCurOnly ", self.client.GetHeaderValue(1), self.client.GetHeaderValue(13))

            self.parent.futCurData.ymd  = com.dtymd
            self.parent.futCurData.item = self.client.GetHeaderValue(0)  # 0 - (string)종목코드
            self.parent.futCurData.close = self.client.GetHeaderValue(1)  # 1 - (double) 현재가
            self.parent.futCurData.diff = self.client.GetHeaderValue(2)  # 2 - (double) 전일대비
            self.parent.futCurData.open = self.client.GetHeaderValue(7)  # 7 - (double) 시가
            self.parent.futCurData.high = self.client.GetHeaderValue(8)  # 8 - (double) 고가
            self.parent.futCurData.low = self.client.GetHeaderValue(9)  # 9 - (double) 저가
            self.parent.futCurData.acc_vol = self.client.GetHeaderValue(13)  # 13 - (long) 누적거래량
            self.parent.futCurData.open_interest = self.client.GetHeaderValue(14)  # 14 - (long) 미결제약정
            self.parent.futCurData.time = self.client.GetHeaderValue(15)  # 15 - (long) 시각

            self.parent.futCurData.fst_offer_prc = self.client.GetHeaderValue(18)  # 18 - (double) 최우선매도호가
            self.parent.futCurData.fst_bid_prc = self.client.GetHeaderValue(19)  # 19 - (double) 최우선매수호가
            self.parent.futCurData.fst_offer_vol = self.client.GetHeaderValue(20)  # 20 - (ulong) 최우선매도호가잔량
            self.parent.futCurData.fst_bid_vol = self.client.GetHeaderValue(21)  # 21 - (ulong) 최우선매수호가잔량
            self.parent.futCurData.acc_offer_vol = self.client.GetHeaderValue(22)  # 22 - (ulong) 누적체결매도
            self.parent.futCurData.acc_bid_vol = self.client.GetHeaderValue(23)  # 23 - (ulong) 누적체결매수
            self.parent.futCurData.prc_sign = chr(self.client.GetHeaderValue(24))  # 24 - (char)체결구분
            self.parent.futCurData.k200_idx = self.client.GetHeaderValue(4)  # 4 - (double) kospi 200 지수

            print(self.parent.futCurData.ymd, self.parent.futCurData.item, self.parent.futCurData.time, self.parent.futCurData.close)

            self.parent.monitorCurPriceChangeFut()

            return

        elif self.name == "pbinvestor":

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

            print("pbinvestor")
            print(self.obj.GetDataValue(0, 0))

            return

        elif self.name == "stockbid":

            print("PB > 종목코드 ", self.client.GetHeaderValue(0))

            # 현재가 10차 호가 데이터 실시간 업데이트
            # append rtMst.offer.append(self.objStockjpbid2.GetDataValue(0, i))  # 매도호가
            # 23 - (long)  총매도잔량
            # 24 - (long)  총매수잔량
            # 25 - (long)  시간외총매도잔량
            # 26 - (long)  시간외총매수잔량

            dataindex = [3, 4, 5, 6,
                         7, 8, 9, 10,
                         11, 12, 13, 14,
                         15, 16, 17, 18,
                         19, 20, 21, 22,
                         27,28,29,30,
                         31,32,33,34,
                         35,36,37,38,
                         39,40,41,42,
                         43,44,45,46]
            obi = 0
            for i in range(10):
                self.parent.stkTickData.ask_prc[i] = self.client.GetHeaderValue(dataindex[obi])        # 0 3 4 7
                self.parent.stkTickData.bid_prc[i] = self.client.GetHeaderValue(dataindex[obi + 1])    # 1 4 5 8
                self.parent.stkTickData.ask_qty[i] = self.client.GetHeaderValue(dataindex[obi+2])      # 2 5 6 9
                self.parent.stkTickData.bid_qty[i] = self.client.GetHeaderValue(dataindex[obi + 3])    # 3 6 7 10

                obi += 4

            self.parent.stkTickData.ymd  = com.dtymd
            self.parent.stkTickData.item = self.client.GetHeaderValue(0)
            self.parent.stkTickData.item_nm = ''
            self.parent.stkTickData.time = self.client.GetHeaderValue(1)
            self.parent.stkTickData.acc_vol = self.client.GetHeaderValue(2)

            self.parent.stkTickData.ask_tot_qty = self.client.GetHeaderValue(23)
            self.parent.stkTickData.bid_tot_qty = self.client.GetHeaderValue(24)
            self.parent.stkTickData.extime_ask_tot_qty = self.client.GetHeaderValue(25)
            self.parent.stkTickData.extime_bid_tot_qty = self.client.GetHeaderValue(26)

            self.parent.monitorTickChange()

            return True

        elif self.name == "conclusion":
            # 주문 체결 실시간 업데이트

            print("+++++++++++++++++++++++++++++++++++++++")
            print("elif self.name == conclusion")
            print("+++++++++++++++++++++++++++++++++++++++")

            self.parent.stkConData.ymd     = com.dtymd
            self.parent.stkConData.con_qty = self.client.GetHeaderValue(3)  # 체결 수량
            self.parent.stkConData.con_prc = self.client.GetHeaderValue(4)  # 가격
            self.parent.stkConData.odr_no = self.client.GetHeaderValue(5)  # 주문번호
            self.parent.stkConData.org_no = self.client.GetHeaderValue(6)  # 6 - (long원주문번호
            self.parent.stkConData.item = self.client.GetHeaderValue(9)  # 종목코드
            self.parent.stkConData.acc_no = self.client.GetHeaderValue(7)  #
            self.parent.stkConData.odr_tp = self.client.GetHeaderValue(12)  # 12 - (string)매매구분코드 bs
            self.parent.stkConData.con_tp = self.client.GetHeaderValue(14)  # 14 - (string) 체결구분코드		che_gb
            self.parent.stkConData.cncl_tp = self.client.GetHeaderValue(16)  # 16?- (string) 정정취소구분코드		ju_gb
            self.parent.stkConData.short_qty = self.client.GetHeaderValue(23)  # 22 -?(long) 매도가능수량
            self.parent.stkConData.blnc_qty = self.client.GetHeaderValue(23)  # 체결 후 잔고 수량

            self.parent.stkConData.strtgy_no = '100'
            self.parent.stkConData.odr_qty = 0
            self.parent.stkConData.odr_prc = 0
            self.parent.stkConData.acc_nm = ' '
            self.parent.stkConData.mtime  = ' '
            self.parent.stkConData.item_nm = ' '

            if self.parent.stkConData.con_tp in self.concdic:
                self.parent.stkConData.con_nm = self.concdic.get(self.parent.stkConData.con_tp)

            if (self.parent.stkConData.odr_tp in self.buyselldic):
                self.parent.stkConData.odr_nm = self.buyselldic.get(self.parent.stkConData.odr_tp)

            print("+++++++++++++++++++++++++++++++++++++++")
            print(self.parent.stkConData.con_nm, self.parent.stkConData.odr_nm, self.parent.stkConData.item, "주문번호:", self.parent.stkConData.odr_no, self.parent.stkConData.con_qty, self.parent.stkConData.con_prc)
            print("+++++++++++++++++++++++++++++++++++++++")

            # call back 함수 호출해서 orderMain 에서 후속 처리 하게 한다.
            #self.parent.monitorConclusion(item, acc_no, con_tp, con_prc, con_qty, blnc_qty, condt)

            self.parent.monitorCon()

            return
# CPevent
###############################################################################
