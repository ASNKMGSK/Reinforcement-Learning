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

import creon_cprobot_comm as com
import creon_cpdata  as CpData
import creon_cpevent as CpEvent
import creon_cpmariadb  as CpDB

###############################################################################
# CpSBConclusion: 실시간 주문 체결 수신 클래그
class CpSBConclusion:
    def __init__(self):
        self.name = "conclusion" # conclusion
        self.obj = win32com.client.Dispatch("DsCbo1.CpConclusion")

    def Subscribe(self, parent):
        self.parent = parent
        handler = win32com.client.WithEvents(self.obj, CpEvent.CpEvent)
        handler.set_params(self.obj, self.name, parent)
        self.obj.Subscribe()

    def Unsubscribe(self):
        self.obj.Unsubscribe()

###############################################################################
# 미체결 조회 서비스
class Cp5339:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpTrade.CpTd5339")
        self.acc_no = com.g_objCpTrade.AccountNumber[0]  # 계좌번호
        self.acc_tp = com.g_objCpTrade.GoodsList(self.acc_no, 1)  # 주식상품 구분

    def Request(self, dicOrderList, orderList):
        self.obj.SetInputValue(0, self.acc_no)
        self.obj.SetInputValue(1, self.acc_tp[0])
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
                item = orderData()
                item.orderNum = self.obj.GetDataValue(1, i)
                item.orderPrev = self.obj.GetDataValue(2, i)
                item.code = self.obj.GetDataValue(3, i)  # 종목코드
                item.name = self.obj.GetDataValue(4, i)  # 종목명
                item.orderDesc = self.obj.GetDataValue(5, i)  # 주문구분내용
                item.amount = self.obj.GetDataValue(6, i)  # 주문수량
                item.price = self.obj.GetDataValue(7, i)  # 주문단가
                item.ContAmount = self.obj.GetDataValue(8, i)  # 체결수량
                item.credit = self.obj.GetDataValue(9, i)  # 신용구분
                item.modAvali = self.obj.GetDataValue(11, i)  # 정정취소 가능수량
                item.buysell = self.obj.GetDataValue(13, i)  # 매매구분코드
                item.creditdate = self.obj.GetDataValue(17, i)  # 대출일
                item.orderFlagDesc = self.obj.GetDataValue(19, i)  # 주문호가구분코드내용
                item.orderFlag = self.obj.GetDataValue(21, i)  # 주문호가구분코드

                # 사전과 배열에 미체결 item 을 추가
                dicOrderList[item.orderNum] = item
                orderList.append(item)

            # 연속 처리 체크 - 다음 데이터가 없으면 중지
            if self.obj.Continue == False:
                print("[Cp5339] 연속 조회 여부: 다음 데이터가 없음")
                break

        return True

################################################
# Cp6033 : 주식 잔고 조회
# class Cp6033:
#     def __init__(self):
#         acc_no = com.g_objCpTrade.AccountNumber[0]  # 계좌번호
#         acc_tp = com.g_objCpTrade.GoodsList(acc_no, 1)  # 주식상품 구분
#
#         print(acc_no, acc_tp[0])
#
#         self.obj = win32com.client.Dispatch("CpTrade.CpTd6033")
#         self.obj.SetInputValue(0, acc_no)  # 계좌번호
#         self.obj.SetInputValue(1, acc_tp[0])  # 상품구분 - 주식 상품 중 첫번째
#         self.obj.SetInputValue(2, 50)  # 요청 건수(최대 50)
#         self.dicflag1 = {ord(' '): '현금',
#                          ord('Y'): '융자',
#                          ord('D'): '대주',
#                          ord('B'): '담보',
#                          ord('M'): '매입담보',
#                          ord('P'): '플러스론',
#                          ord('I'): '자기융자',
#                          }
#
#     # 실제적인 6033 통신 처리
#     def request(self, caller):
#         while True:
#             self.obj.BlockRequest()
#             # 통신 및 통신 에러 처리
#             rqStatus = self.obj.GetDibStatus()
#             rqRet = self.obj.GetDibMsg1()
#             print("통신상태", rqStatus, rqRet)
#             if rqStatus != 0:
#                 return False
#
#             cnt = self.obj.GetHeaderValue(7)
#
#             print("Cp6033 request", cnt)
#
#             for i in range(cnt):
#                 blnc = {}
#                 item_cd = self.obj.GetDataValue(12, i)  # 종목코드
#                 blnc['item_cd'] = item_cd
#                 blnc['item_nm'] = self.obj.GetDataValue(0, i)  # 종목명
#                 blnc['crdt_tp'] = self.dicflag1[self.obj.GetDataValue(1, i)]  # 신용구분
#                 # item['대출일'] = self.obj.GetDataValue(2, i)  # 대출일
#                 blnc['yd_qty'] = self.obj.GetDataValue(5, i)  # 전일체결잔고수량
#                 blnc['td_qty'] = self.obj.GetDataValue(6, i)  # 금일체결잔고수량
#                 blnc['qty'] = self.obj.GetDataValue(7, i)  # 체결잔고수량
#                 blnc['short_qty'] = self.obj.GetDataValue(15, i) # 매도가능수량
#                 blnc['book_prc'] = self.obj.GetDataValue(17, i)  # 체결장부단가
#                 blnc['val_amt'] = self.obj.GetDataValue(9, i)  # 평가금액(천원미만은 절사 됨)
#                 blnc['val_pl'] = self.obj.GetDataValue(11, i)  # 평가손익(천원미만은 절사 됨)
#
#                 # 매입금액 = 장부가 * 잔고수량
#                 blnc['long_amt'] = blnc['book_prc'] * blnc['qty']
#
#                 # 잔고 추가
#                 #                key = (code, item['현금신용'],item['대출일'] )
#                 key = item_cd
#                 caller.jangoData[key] = item_cd
#
#                 if len(caller.jangoData) >= 200:  # 최대 200 종목만,
#                     break
#
#             if len(caller.jangoData) >= 200:
#                 break
#             if (self.obj.Continue == False):
#                 break
#
#         return True