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

import creon_cpcomm as com
import creon_cpdata  as CpData
import creon_cpevent as CpEvent
import creon_cpmariadb  as CpDB

###############################################################################
# 주문결과
class StkOdrRsltData:
    def __init__(self):
        self.ymd = ''
        self.odr_tp = ''
        self.acc_no = ''
        self.prdt_tp = ''
        self.item = ''
        self.qty = 0
        self.prc = 0
        self.odr_no = 0
        self.acc_nm = ''
        self.item_nm = ''
        self.cond_tp = ''
        self.odr_tick_tp = ''
        self.msg = ''

###############################################################################
# 잔고 저장 변수
class StkBlncData:
    def __init__(self):
        self.ymd = []
        self.acc_no = []
        self.item = []
        self.item_nm = []
        self.con_qty = []
        self.con_prc = []
        self.td_qty = []
        self.yd_qty = []
        self.qty = []
        self.short_qty = []
        self.book_prc = []
        self.val_amt = []
        self.pl_amt = []

###############################################################################
# 체결데이터
class StkConData:
    def __init__(self):
        self.ymd      = ''
        self.item     = ''
        self.acc_no   = 0
        self.strtgy_no = 0
        self.item     = 0
        self.odr_no   = 0
        self.org_no = 0
        self.con_qty  = 0
        self.con_prc = 0
        self.odr_tp   = 0
        self.con_tp   = 0
        self.cncl_tp  = 0
        self.short_qty = 0
        self.blnc_qty = 0
        self.odr_qty = 0
        self.odr_nm   = ''
        self.con_nm   = ''
        self.odr_prc  = ''
        self.acc_nm = ''
        self.item_nm = ''
        self.mtime   = ''

###############################################################################
# 미체결 주문 정보 저장 구조체
class StkUnConData:
    def __init__(self):
        self.item = []  # 종목코드
        self.item_nm = []  # 종목명
        self.odr_no = []  # 주문번호
        self.org_no = []  # 원주문번호
        self.odr_desc = []  # 주문구분내용
        self.qty = []  # 주문수량
        self.prc = []  # 주문 단가
        self.con_qty = []  # 체결수량
        self.crdt_tp = []  # 신용 구분 "현금" "유통융자" "자기융자" "유통대주" "자기대주"
        self.mod_qty = []  # 정정/취소 가능 수량
        self.odr_tp = []  # 매매구분 코드  1 매도 2 매수
        self.crdt_ymd = []  # 대출일
        self.odr_tick_tp = []  # 주문호가 구분코드
        self.odr_tick_desc = []  # 주문호가 구분 코드 내용

        # 데이터 변환용
        self.concdic    = {"1": "체결", "2": "확인", "3": "거부", "4": "접수"}
        self.buyselldic = {"1": "매도", "2": "매수"}

###############################################################################
# 전략 저장 변수
class StrtgyData:
    def __init__(self):
        self.ymd = []
        self.strtgy_no = []
        self.item = []
        self.exec_tp = []
        self.rslt_tp = []
        self.con_tp = []
        self.can_tp = []
        self.odr_tp = []
        self.qty = []
        self.prc = []
        self.msg = []
        self.stgy_msg = []
        self.errCnt = 10
        self.odr_no = 0
        self.tp = ''
        self.term = 0
        self.ma5 = 0
        self.ma10 = 0
        self.ma20 = 0
        self.ma60 = 0
        self.ma120 = 0
        self.ma240 = 0
        self.vol_avg = 0
        self.vol_std = 0

###############################################################################
# class CpConclusionExec:
#     def __init__(self):
#         #####################################################################
#         # object
#         self.objSBCon = CpSBConclusion()
#         self.objSBCon.Subscribe(self)
#
#     def monitorConclusion(self):
#         pass

###############################################################################
# CpSBConclusion: 실시간 주문 체결 수신 클래그
class CpSBConclusion:
    def __init__(self):

        self.name = "conclusion"  # conclusion

    def Subscribe(self, stkConData, parent):

        pythoncom.CoInitialize()
        self.obj = win32com.client.Dispatch("DsCbo1.CpConclusion")

        print("def Subscribe(self, stkConData, parent):")

        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()
        self.stkConData = stkConData

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
class CpOrderExec:
    def __init__(self):

        self.isSB = False  # 실시간 처리

        #####################################################################
        # data
        self.stkCurData   = CpData.StkCurData()
        self.stkTickData  = CpData.StkTickData()  # 주문 현재가/10차 호가 저장
        self.strtgyData   = StrtgyData()
        self.strtgyDataT  = StrtgyData()
        self.stkBlncData  = StkBlncData()

        ###############################################################################
        # 주문결과
        self.stkOdrRsltData = StkOdrRsltData()

        #####################################################################
        # object
        self.objOdr   = CpOrder()
        self.objSBcur = CpData.CpSBStockCur()
        self.objSBbid = CpData.CpSBStockBid()
        self.objCurBid  = CpData.CpStockCurBid()
        self.objCurBid2 = CpData.CpStockCurBid2()
        self.objDB      = CpDB.CpDB()

        #####################################################################
        # 잔고조회 / 미체결조회
        self.objBlnc  = Cp6033()
        self.objUnCon = Cp5339()

    def stopSubscribe(self):
        if self.isSB:
            self.objSBcur.Unsubscribe()
            self.objSBbid.Unsubscribe()

        self.isSB = False

    def monitorTickChange(self):
        print("=====================================================")
        print("monitorTickChange ", self.stkTickData.ask_prc[0], self.stkTickData.bid_prc[0])
        print("=====================================================")

        return

    ###############################################################################
    # 잔고조회 self.stkBlncData
    # if self.objCurBid.Request(item, self.stkTickData) == False:
    def getBlncData(self, tp, acc_no, odata):
        if self.objBlnc.Request(acc_no, odata) == False:
            return odata

        return odata

    def getBlncQty(self, tp, acc_no, item, odata):
        if self.objBlnc.Request(acc_no, odata) == False:
            return odata

        cnt = len(odata.item)
        for i in range(cnt):
            print("BLNC ", odata.item[i], odata.con_qty[i])
            if odata.item[i] == item:
                return int(odata.con_qty[i])

        return 0

    ###############################################################################
    # 취소주문 실행
    async def canorder_async(self, acc_no, dicOdrList, odrList):
        while True:
            remainCount = com.g_objCpStatus.GetLimitRemainCount(1)  # 1 시세 제한
            if remainCount <= 0:
                print('시세 연속 조회 제한 회피를 위해 sleep', com.g_objCpStatus.LimitRequestRemainTime)
                await asyncio.sleep(com.g_objCpStatus.LimitRequestRemainTime / 1000)

            ###############################################################################
            # 미체결조회
            if self.objUnCon.Request(acc_no, dicOdrList, odrList) == False:
                print("현재가 통신 실패")
                return

            cnt = len(odrList.item)
            for i in range(cnt):
                print("canorder_async 주문정보 : %s, %s" % (odrList.item[i], odrList.item_nm[i]))

                ###############################################################################
                # 현재가 / 호가 조회 : offer  매도 / bid / 매수
                # Data Class 초기화 하는 방법
                # self.stopSubscribe()
                self.stkTickData = CpData.StkTickData()  # 주문 현재가/10차 호가 저장
                if self.objCurBid.Request(odrList.item[i], self.stkTickData) == False:
                    print("현재가 통신 실패")
                    return

                ###############################################################################
                # 5호가 차이 취소 매도 매도가격이 5호가 보다 크면 취소
                if odrList.odr_tp[i] == '1':
                    if odrList.prc[i] >= self.stkTickData.offer[5-1]:
                        print("매도취소주문 실행 ", odrList.item[i], "현재가", self.stkTickData.cur, "주문가격", odrList.prc[i], "1차매도호가",
                              self.stkTickData.offer[0], "1차매수호가", self.stkTickData.bid_prc[0])

                        bResult = self.objOdr.canOrder(acc_no, odrList.item[i], odrList.mod_qty[i], odrList.prc[i], odrList.odr_no[i])
                        if bResult == False:
                            print("주문 실패")
                            return

                ###############################################################################
                # 매수
                if odrList.odr_tp[i] == '2':
                    if odrList.prc[i] <= self.stkTickData.bid_prc[5-1]:
                        print("매수취소주문 실행", odrList.item[i], "현재가", self.stkTickData.cur, "주문가격", odrList.prc[i], "1차매도호가",
                              self.stkTickData.offer[0], "1차매수호가", self.stkTickData.bid_prc[0])

                        bResult = self.objOdr.canOrder(acc_no, odrList.item[i], odrList.mod_qty[i], odrList.prc[i], odrList.odr_no[i])
                        if bResult == False:
                            print("주문 실패")
                            return

                print("조회 취소주문", odrList.item[i], "현재가", self.stkTickData.cur, "주문가격", odrList.prc[i], "1차매도호가",
                      self.stkTickData.offer[0], "1차매수호가", self.stkTickData.bid_prc[0])


            await asyncio.sleep(5)

    def my_coroutine(self, task_name, seconds_to_sleep=3):
        print('{0} sleeping for: {1} seconds'.format(task_name, seconds_to_sleep))
        time.sleep(seconds_to_sleep)
        print('{0} is finished'.format(task_name))

    ###############################################################################
    # 매수주문
    def order_thread(self, acc_no):
        errCnt = 0
        idata = {}

        while True:
            remainCount = com.g_objCpStatus.GetLimitRemainCount(1)  # 1 시세 제한
            if remainCount <= 0:
                print('시세 연속 조회 제한 회피를 위해 sleep', com.g_objCpStatus.LimitRequestRemainTime)
                time.sleep(com.g_objCpStatus.LimitRequestRemainTime / 1000)

            ###############################################################################
            # 전략 조회
            self.objDB.stkstrtgy('S', self, self.strtgyDataT)
            cnt = len(self.strtgyDataT.ymd)

            print("*********************************************")
            print("order_thread cnt ", cnt)
            print("*********************************************")

            for i in range(cnt):
                print("self.StrtgyDataT", len(self.strtgyDataT.ymd), i, self.strtgyDataT.ymd[i], self.strtgyDataT.item[i])

                self.strtgyData.ymd       = self.strtgyDataT.ymd[i]
                self.strtgyData.strtgy_no = self.strtgyDataT.strtgy_no[i]
                self.strtgyData.item      = self.strtgyDataT.item[i]
                self.strtgyData.exec_tp   = self.strtgyDataT.exec_tp[i]
                self.strtgyData.rslt_tp   = self.strtgyDataT.rslt_tp[i]
                self.strtgyData.con_tp    = self.strtgyDataT.con_tp[i]
                self.strtgyData.can_tp    = self.strtgyDataT.can_tp[i]

                self.strtgyData.odr_tp    = self.strtgyDataT.odr_tp[i]
                self.strtgyData.qty       = self.strtgyDataT.qty[i]
                self.strtgyData.prc       = self.strtgyDataT.prc[i]
                self.strtgyData.msg       = self.strtgyDataT.msg[i]

                if self.strtgyData.exec_tp == 'N':

                    ###############################################################################
                    # 매매 정보
                    item = self.strtgyData.item

                    buy_qty = 0
                    buy_price = 0
                    sel_qty = 0
                    sel_price = 0

                    if self.strtgyData.odr_tp == '2':
                        buy_qty = self.strtgyData.qty
                        buy_price = self.strtgyData.prc

                    if self.strtgyData.odr_tp == '1':
                        sel_qty = self.strtgyData.qty
                        sel_price = self.strtgyData.prc

                    ###############################################################################
                    # Subscribe 가 아닌 Request 데이터 사용
                    #self.stopSubscribe()
                    if self.objCurBid.Request(item, self.stkTickData) == False:
                        print("현재가 통신 실패")
                        time.sleep(1)
                        errCnt = errCnt + 1

                    else:
                        ###############################################################################
                        # 매수 주문
                        if self.strtgyData.odr_tp == '2':

                            print("조회 매수주문", item, "현재가", self.stkTickData.cur, "매수가", buy_price, "매도가", sel_price, "1차매도호가",
                                  self.stkTickData.ask_prc[0], "1차매수호가", self.stkTickData.bid_prc[0])

                            if self.stkTickData.cur != 0 and self.stkTickData.cur <= buy_price:  # and self.stkTickData.cur <= self.stkTickData.bid_prc[0]:

                                print("신규 매수주문 EXEC ", item, buy_price, self.stkTickData.ask_prc[0], self.stkTickData.bid_prc[0])

                                ###############################################################################
                                # 매수 주문전 주문 가능금액 확인
                                bResult = self.objOdr.buyOrder(acc_no, item, buy_qty, buy_price, self.stkOdrRsltData)
                                if bResult == False:
                                    errCnt = errCnt + 1

                                    self.strtgyData.exec_tp = 'Y'
                                    self.strtgyData.rslt_tp = 'N'
                                    self.strtgyData.odr_no = self.stkOdrRsltData.odr_no
                                    self.strtgyData.msg = str(self.stkOdrRsltData.odr_no) + " : " + self.stkOdrRsltData.msg

                                    print("주문 실패 self.objOdr.buyOrder", self.strtgyData.exec_tp, self.strtgyData.rslt_tp, self.strtgyData.msg)

                                    self.objDB.stkstrtgy('F', self.strtgyData, self.strtgyData)

                                else:
                                    ###############################################################################
                                    # 주문 확인 주문상태 업데이트
                                    # exec_tp = 'Y' , rslt_tp = 'Y'
                                    ###############################################################################
                                    # 주문 확인 주문상태 업데이트
                                    self.strtgyData.exec_tp = 'Y'
                                    self.strtgyData.rslt_tp = 'Y'
                                    self.strtgyData.odr_no = self.stkOdrRsltData.odr_no
                                    self.strtgyData.msg = str(self.stkOdrRsltData.odr_no) + " : " + self.stkOdrRsltData.msg

                                    self.stkOdrRsltData.strtgy_no = self.strtgyData.strtgy_no

                                    print("매수 결과 ", self.strtgyData.rslt_tp, self.stkOdrRsltData.ymd,self.stkOdrRsltData.acc_no, self.strtgyData.msg)

                                    ###############################################################################
                                    # 최초 주문 접수
                                    self.objDB.stkstrtgy('F', self.strtgyData, self.strtgyData)
                                    self.objDB.stkodr('I', self.stkOdrRsltData, self.stkOdrRsltData)

                        ###############################################################################
                        # 매도 주문
                        if self.strtgyData.odr_tp == '1':

                            print("조회 매도주문", item, "현재가", self.stkTickData.cur, "매수가", buy_price, "매도가", sel_price,
                                  "1차매도호가", self.stkTickData.ask_prc[0], "1차매수호가", self.stkTickData.bid_prc[0])

                            if self.stkTickData.cur != 0 and self.stkTickData.cur >= sel_price:  # and self.stkTickData.cur <= self.stkTickData.bid_prc[0]:

                                print("신규 매도주문 EXEC ", item, sel_price, self.stkTickData.ask_prc[0], self.stkTickData.bid_prc[0])

                                ###############################################################################
                                # 매도 주문전 주문 잔고 확인
                                #self.objBlnc.Request(acc_no, self.stkBlncData)
                                blnc_qty = 0
                                blnc_qty = self.getBlncQty('I', acc_no, item, self.stkBlncData)
                                if  blnc_qty <= 0:
                                    print("주문 실패 잔고부족 ", item, blnc_qty)

                                    self.strtgyData.exec_tp = 'Y'
                                    self.strtgyData.rslt_tp = 'N'
                                    self.strtgyData.msg     = "주문 실패 잔고부족"
                                    self.objDB.stkstrtgy('F', self.strtgyData, self.strtgyData)

                                    continue

                                print("주문 잔고 ", item, blnc_qty)

                                # 잔고수량 확인후 변경
                                if sel_qty >= blnc_qty :
                                    sel_qty = blnc_qty

                                bResult = self.objOdr.selOrder(acc_no, item, sel_qty, sel_price, self.stkOdrRsltData)
                                if bResult == False:
                                    print("주문 실패 self.objOdr.selOrder 1", self.stkOdrRsltData.msg)
                                    errCnt = errCnt + 1

                                    self.strtgyData.exec_tp = 'Y'
                                    self.strtgyData.rslt_tp = 'N'
                                    self.strtgyData.odr_no = self.stkOdrRsltData.odr_no
                                    self.strtgyData.msg = str(self.stkOdrRsltData.odr_no) + " : " + self.stkOdrRsltData.msg
                                    self.objDB.stkstrtgy('F', self.strtgyData, self.strtgyData)

                                    print("주문 실패 self.objOdr.selOrder 2", self.stkOdrRsltData.msg, self.strtgyData.exec_tp, self.strtgyData.msg)

                                else:
                                    ###############################################################################
                                    # 주문 확인 주문상태 업데이트
                                    self.strtgyData.exec_tp = 'Y'
                                    self.strtgyData.rslt_tp = 'Y'
                                    self.strtgyData.odr_no = self.stkOdrRsltData.odr_no
                                    self.strtgyData.msg = str(self.stkOdrRsltData.odr_no) + " : " + self.stkOdrRsltData.msg

                                    self.stkOdrRsltData.strtgy_no = self.strtgyData.strtgy_no

                                    print("매도 결과 ", self.strtgyData.rslt_tp, self.stkOdrRsltData.ymd, self.stkOdrRsltData.acc_no, self.strtgyData.msg)

                                    ###############################################################################
                                    # 최초 주문 접수
                                    self.objDB.stkstrtgy('F', self.strtgyData, self.strtgyData)
                                    self.objDB.stkodr('I', self.stkOdrRsltData, self.stkOdrRsltData)

                # 실시간 통신 요청
                # self.objSBcur.Subscribe(item, self.stkCurData , self)
                # self.objSBbid.Subscribe(item, self.stkTickData, self)
                # self.isSB = True    # 주문 실행 end
            # for end

            time.sleep(3)

###############################################################################
class CpOrder:
    def __init__(self):
        # 매수/정정/취소 주문 object 생성
        self.objMdifyOdr = win32com.client.Dispatch("CpTrade.CpTd0313")  # 정정
        self.objCancelOdr = win32com.client.Dispatch("CpTrade.CpTd0314")  # 취소
        self.order_num = 0 # 주문 번호

    ###############################################################################
    # 계좌 종목 수량 가격
    def selOrder(self, acc_no, item, qty, price, odata):

        self.objSelOdr = win32com.client.Dispatch("CpTrade.CpTd0311")  # 매도

        # 주식 매도 주문
        print("신규 매도", item, qty, price)
        
        # 주식 매도 주문
        self.objSelOdr.SetInputValue(0, "1")   #  1: 매도
        self.objSelOdr.SetInputValue(1, acc_no )   #  계좌번호
        self.objSelOdr.SetInputValue(2, "10")   #  상품구분 - 주식 상품 중 첫번째
        self.objSelOdr.SetInputValue(3, item)   #  종목코드 - A003540 - 대신증권 종목
        self.objSelOdr.SetInputValue(4, qty)   #  매도수량 10주
        self.objSelOdr.SetInputValue(5, price)   #  주문단가  - 14,100원
        self.objSelOdr.SetInputValue(7, "0")   #  주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
        self.objSelOdr.SetInputValue(8, "01")   # 주문호가 구분코드 - 01: 보통
     
        # 매도 주문 요청
        self.objSelOdr.BlockRequest()
 
        rqStatus = self.objSelOdr.GetDibStatus()
        rqRet = self.objSelOdr.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        odata.msg = rqRet
        if rqStatus != 0:
            return False

        odata.ymd = com.dtymd
        odata.odr_tp = self.objSelOdr.GetHeaderValue(0)  # 0 - (string) 주문종류코드
        odata.acc_no = self.objSelOdr.GetHeaderValue(1)  # 1 - (string) 계좌번호
        odata.prdt_no = self.objSelOdr.GetHeaderValue(2)  # 2 - (string) 상품관리구분코드
        odata.item = self.objSelOdr.GetHeaderValue(3)  # 3 - (string) 종목코드
        odata.qty = self.objSelOdr.GetHeaderValue(4)  # 4 - (long) 주문수량
        odata.prc = self.objSelOdr.GetHeaderValue(5)  # 5 - (long) 주문단가
        odata.odr_no = self.objSelOdr.GetHeaderValue(8)  # 8 - (long) 주문번호
        odata.acc_nm = self.objSelOdr.GetHeaderValue(9)  # 9 - (string) 계좌명
        odata.item_nm = self.objSelOdr.GetHeaderValue(10)  # 10 - (string) 종목명
        odata.cond_tp = self.objSelOdr.GetHeaderValue(12)  # 12 - (string) 주문조건구분코드
        odata.odr_tick_tp = self.objSelOdr.GetHeaderValue(13)  # 13 - (string) 주문호가구분코드

        # self.prdt_tp = ''
        # self.item = ''
        # self.qty = 0
        # self.prc = 0
        # self.odr_no = 0
        # self.acc_nm = ''
        # self.item_nm = ''
        # self.cond_tp = ''
        # self.odr_tick_tp = ''

        print("def selOrder(self, acc_no, item, qty, price, odata)", odata.ymd, odata.odr_tp, odata.acc_no)

        # 주의: 매수 주문에  대한 구체적인 처리는 cpconclusion 으로 파악해야 한다.
        return True

    ###############################################################################
    # 계좌 종목 수량 가격
    def buyOrder(self, acc_no, item, qty, price, odata):
        # 주식 매수 주문
        print("신규 매수", item, price, qty)

        self.objBuyOdr = win32com.client.Dispatch("CpTrade.CpTd0311")  # 매수

        self.objBuyOdr.SetInputValue(0, "2")  # 2: 매수
        self.objBuyOdr.SetInputValue(1, acc_no)  # 계좌번호
        self.objBuyOdr.SetInputValue(2, "10")  # self.acc_tp[0] 상품구분 - 주식 상품 중 첫번째
        self.objBuyOdr.SetInputValue(3, item)  # 종목코드
        self.objBuyOdr.SetInputValue(4, qty)  # 매수수량
        self.objBuyOdr.SetInputValue(5, price)  # 주문단가 
        self.objBuyOdr.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
        self.objBuyOdr.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통
 
        # 매수 주문 요청
        self.objBuyOdr.BlockRequest()
 
        rqStatus = self.objBuyOdr.GetDibStatus()
        rqRet = self.objBuyOdr.GetDibMsg1()

        print("통신상태", rqStatus, rqRet)
        odata.msg = rqRet
        if rqStatus != 0:
            odata.msg = rqRet
            return False

        odata.ymd = com.dtymd
        odata.odr_tp = self.objBuyOdr.GetHeaderValue(0)  # 0 - (string) 주문종류코드
        odata.acc_no = self.objBuyOdr.GetHeaderValue(1)  # 1 - (string) 계좌번호
        odata.prdt_no = self.objBuyOdr.GetHeaderValue(2)  # 2 - (string) 상품관리구분코드
        odata.item = self.objBuyOdr.GetHeaderValue(3)  # 3 - (string) 종목코드
        odata.qty = self.objBuyOdr.GetHeaderValue(4)  # 4 - (long) 주문수량
        odata.prc = self.objBuyOdr.GetHeaderValue(5)  # 5 - (long) 주문단가
        odata.odr_no = self.objBuyOdr.GetHeaderValue(8)  # 8 - (long) 주문번호
        odata.acc_nm = self.objBuyOdr.GetHeaderValue(9)  # 9 - (string) 계좌명
        odata.item_nm = self.objBuyOdr.GetHeaderValue(10)  # 10 - (string) 종목명
        odata.cond_tp = self.objBuyOdr.GetHeaderValue(12)  # 12 - (string) 주문조건구분코드
        odata.odr_tick_tp = self.objBuyOdr.GetHeaderValue(13)  # 13 - (string) 주문호가구분코드

        # 주의: 매수 주문에  대한 구체적인 처리는 cpconclusion 으로 파악해야 한다.
        return True

    ###############################################################################
    # 계좌 종목 수량 가격 주문번호 잔량전체체
    def mdyOrder(self, acc_no, item, qty, prc, odr_no):
        # 주식 정정 주문
        print("정정주문", ord_no, item, prc)
        self.objModifyOdr.SetInputValue(1, odr_no)     #  원주문 번호 - 정정을 하려는 주문 번호
        self.objModifyOdr.SetInputValue(2, acc_no)           # 상품구분 - 주식 상품 중 첫번째
        self.objModifyOdr.SetInputValue(3, "10")     # 상품구분 - 주식 상품 중 첫번째
        self.objModifyOdr.SetInputValue(4, item)          # 종목코드
        self.objModifyOdr.SetInputValue(5, 0)             # 정정 수량, 0 이면 잔량 정정임
        self.objModifyOdr.SetInputValue(6, prc)         #  정정주문단가
 
        # 정정주문 요청
        self.objModifyOdr.BlockRequest()
 
        rqStatus = self.objModifyOdr.GetDibStatus()
        rqRet = self.objModifyOdr.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False
 
        # 새로운 주문 번호 구한다.
        self.order_num = self.objModifyOdr.GetHeaderValue(7)

    ###############################################################################
    # 계좌 종목 수량 가격 주문번호 잔량전체체
    def canOrder(self, acc_no, item, qty, prc, odr_no):
        # 주식 취소 주문
        print("취소주문", acc_no, odr_no, item)
        self.objCancelOdr.SetInputValue(1, odr_no)  #  원주문 번호 - 정정을 하려는 주문 번호
        self.objCancelOdr.SetInputValue(2, acc_no)  # 상품구분 - 주식 상품 중 첫번째
        self.objCancelOdr.SetInputValue(3, "10")  # 상품구분 - 주식 상품 중 첫번째
        self.objCancelOdr.SetInputValue(4, item)  # 종목코드
        self.objCancelOdr.SetInputValue(5, 0)  # 정정 수량, 0 이면 잔량 취소임
 
        # 취소주문 요청
        self.objCancelOdr.BlockRequest()
 
        rqStatus = self.objCancelOdr.GetDibStatus()
        rqRet = self.objCancelOdr.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

###############################################################################
# 미체결 조회 서비스
class Cp5339:
    def __init__(self):
        pass

    def Request(self, acc_no, dicOdrList, odrList):

        self.obj = win32com.client.Dispatch("CpTrade.CpTd5339")

        self.obj.SetInputValue(0, acc_no)
        self.obj.SetInputValue(1, "10")
        self.obj.SetInputValue(4, "0")  # 전체
        self.obj.SetInputValue(5, "1")  # 정렬 기준 - 역순
        self.obj.SetInputValue(6, "0")  # 전체
        self.obj.SetInputValue(7, 20)   # 요청 개수 - 최대 20개

        print("[Cp5339] 미체결 데이터 조회 시작")
        # 미체결 연속 조회를 위해 while 문 사용
        while True:
            ret = self.obj.BlockRequest()
            if self.obj.GetDibStatus() != 0:
                print("통신상태", self.obj.GetDibStatus(), self.obj.GetDibMsg1())
                return False

            if (ret == 2 or ret == 3):
                print("통신 오류", ret)
                return False;

            # 통신 초과 요청 방지에 의한 요류 인 경우
            while (ret == 4):  # 연속 주문 오류 임. 이 경우는 남은 시간동안 반드시 대기해야 함.
                remainTime = com.g_objCpStatus.LimitRequestRemainTime
                print("연속 통신 초과에 의해 재 통신처리 : ", remainTime / 1000, "초 대기")
                time.sleep(remainTime / 1000)
                ret = self.obj.BlockRequest()

            # 수신 개수
            cnt = self.obj.GetHeaderValue(5)
            print("[Cp5339] 수신 개수 ", cnt)
            if cnt == 0:
                break

            for i in range(cnt):
                odrList.odr_no.append(self.obj.GetDataValue(1, i))
                odrList.org_no.append(self.obj.GetDataValue(2, i))
                odrList.item.append(self.obj.GetDataValue(3, i))  # 종목코드
                odrList.item_nm.append(self.obj.GetDataValue(4, i))  # 종목명
                odrList.odr_desc.append(self.obj.GetDataValue(5, i))  # 주문구분내용
                odrList.qty.append(self.obj.GetDataValue(6, i))  # 주문수량
                odrList.prc.append(self.obj.GetDataValue(7, i))  # 주문단가
                odrList.con_qty.append(self.obj.GetDataValue(8, i))  # 체결수량
                odrList.crdt_tp.append(self.obj.GetDataValue(9, i))  # 신용구분
                odrList.mod_qty.append(self.obj.GetDataValue(11, i))  # 정정취소 가능수량
                odrList.odr_tp.append(self.obj.GetDataValue(13, i))  # 매매구분코드
                odrList.crdt_ymd.append(self.obj.GetDataValue(17, i))  # 대출일
                odrList.odr_tick_tp.append(self.obj.GetDataValue(19, i))  # 주문호가구분코드내용
                odrList.odr_tick_desc.append(self.obj.GetDataValue(21, i))  # 주문호가구분코드

                # 사전과 배열에 미체결 item 을 추가
                # dicOdrList[stkUnConData.odr_no] = stkUnConData
                # odrList.append(stkUnConData)

            # 연속 처리 체크 - 다음 데이터가 없으면 중지
            if self.obj.Continue == False:
                print("[Cp5339] 연속 조회 여부: 다음 데이터가 없음")
                break

        return True

################################################
# Cp6033 : 주식 잔고 조회
class Cp6033:
    def __init__(self):
        pass

    # 실제적인 6033 통신 처리
    def Request(self, acc_no, data):

        print("Cp6033 Request", acc_no)

        self.obj = win32com.client.Dispatch("CpTrade.CpTd6033")

        self.obj.SetInputValue(0, acc_no)  # 계좌번호
        self.obj.SetInputValue(1, '10')  # 상품구분 - 주식 상품 중 첫번째
        self.obj.SetInputValue(2, 50)  # 요청 건수(최대 50)
        self.dicflag1 = {ord(' '): '현금',
                         ord('Y'): '융자',
                         ord('D'): '대주',
                         ord('B'): '담보',
                         ord('M'): '매입담보',
                         ord('P'): '플러스론',
                         ord('I'): '자기융자',
                         }

        while True:
            ret = self.obj.BlockRequest()

            # 통신 및 통신 에러 처리
            rqStatus = self.obj.GetDibStatus()
            rqRet = self.obj.GetDibMsg1()

            print("통신상태 ", ret, rqStatus, rqRet)

            if rqStatus != 0:
                return False

            if (ret == 2 or ret == 3):
                print("통신 오류", ret)
                return False;

            # 통신 초과 요청 방지에 의한 요류 인 경우
            while (ret == 4):  # 연속 주문 오류 임. 이 경우는 남은 시간동안 반드시 대기해야 함.
                remainTime = com.g_objCpStatus.LimitRequestRemainTime
                print("연속 통신 초과에 의해 재 통신처리 : ", remainTime / 1000, "초 대기")
                time.sleep(remainTime / 1000)
                ret = self.obj.BlockRequest()

            cnt = self.obj.GetHeaderValue(7)

            print("cnt = self.obj.GetHeaderValue(7) ", cnt)

            for i in range(cnt):
                data.acc_no.append(acc_no)  # 게좌
                data.item.append(self.obj.GetDataValue(12, i))      # 종목코드
                data.item_nm.append(self.obj.GetDataValue(0, i))    # 종목명
                data.con_qty.append(self.obj.GetDataValue(7, i))        # 체결잔고수량
                data.td_qty.append(self.obj.GetDataValue(6, i))     # 금일체결잔고수량
                data.yd_qty.append(self.obj.GetDataValue(5, i))     # 전일체결잔고수량
                data.con_prc.append(self.obj.GetDataValue(17, i))   # 체결장부단가
                data.val_amt.append(self.obj.GetDataValue(9, i))    # 평가금액(천원미만은 절사 됨)
                data.pl_amt.append(self.obj.GetDataValue(11, i))    # 평가손익(천원미만은 절사 됨)

                print(data.item[i], data.con_qty[i])

                # blnc = {}
                # item = self.obj.GetDataValue(12, i)  # 종목코드
                # blnc['item'] = item
                # blnc['item_nm'] = self.obj.GetDataValue(0, i)  # 종목명
                # blnc['crdt_tp'] = self.dicflag1[self.obj.GetDataValue(1, i)]  # 신용구분
                # # item['대출일'] = self.obj.GetDataValue(2, i)  # 대출일
                # blnc['qty'] = self.obj.GetDataValue(7, i)  # 체결잔고수량
                # blnc['qty'] = self.obj.GetDataValue(15, i)
                # blnc['book_prc'] = self.obj.GetDataValue(17, i)  # 체결장부단가
                # blnc['val_amt'] = self.obj.GetDataValue(9, i)  # 평가금액(천원미만은 절사 됨)
                # blnc['val_pl'] = self.obj.GetDataValue(11, i)  # 평가손익(천원미만은 절사 됨)
                #
                # # 매입금액 = 장부가 * 잔고수량
                # blnc['long_amt'] = blnc['book_prc'] * blnc['qty']
                #
                # # 잔고 추가
                # #                key = (code, item['현금신용'],item['대출일'] )
                # key = item
                # caller.jangoData[key] = item
                #
                # if len(caller.jangoData) >= 200:  # 최대 200 종목만,
                #     break

            if len(data.item) >= 200:
                break
            if (self.obj.Continue == False):
                break

        return True