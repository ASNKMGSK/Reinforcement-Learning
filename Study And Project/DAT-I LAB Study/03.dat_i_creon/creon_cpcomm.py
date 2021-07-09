import sys
import signal
from PyQt5.QtWidgets import *
import win32com.client
import asyncio
import threading
from time import sleep
import ctypes
import os
import pythoncom
import datetime
import win32event
import time


#pycrypto
#from Crypto import Random
#from Crypto.Cipher import AES

import json
import hashlib
import base64
import logging

def signal_handler(signal, frame):  # SIGINT handler정의
    print('You pressed Ctrl+C!')
    sys.exit(0)
        
###############################################################################
#   PLUS 공통 OBJECT
#pythoncom.CoInitializeEx(0) 

g_objCodeMgr  = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade  = win32com.client.Dispatch('CpTrade.CpTdUtil')

g_objElwMgr = win32com.client.Dispatch("CpUtil.CpElwCode")
g_objFutureMgr = win32com.client.Dispatch("CpUtil.CpFutureCode")
g_objOptionMgr = win32com.client.Dispatch("CpUtil.CpOptionCode")
g_objCpUtil = win32com.client.Dispatch("CpUtil.CpCybos")

objShell = win32com.client.Dispatch("Shell.Application")


StopEvent = win32event.CreateEvent(None, 0, 0, None)
def MessagePump(timeout):
    waitables = [StopEvent]
    while 1:
        rc = win32event.MsgWaitForMultipleObjects(
            waitables,
            0,  # Wait for all = false, so it waits for anyone
            timeout,  # (or win32event.INFINITE)
            win32event.QS_ALLEVENTS)  # Accepts all input

        if rc == win32event.WAIT_OBJECT_0:
            # Our first event listed, the StopEvent, was triggered, so we must exit
            print('stop event')
            break

        elif rc == win32event.WAIT_OBJECT_0 + len(waitables):
            # A windows message is waiting - take care of it. (Don't ask me
            # why a WAIT_OBJECT_MSG isn't defined < WAIT_OBJECT_0...!).
            # This message-serving MUST be done for COM, DDE, and other
            # Windowsy things to work properly!
            print('pump')
            if pythoncom.PumpWaitingMessages():
                break  # we received a wm_quit message
        elif rc == win32event.WAIT_TIMEOUT:
            print('timeout')
            return
            pass
        else:
            print('exception')
            raise RuntimeError("unexpected win32wait return value")

###############################################################################
# 전일 대비 계산
def getLimitTime():
    remainCount = g_objCpStatus.GetLimitRemainCount(1)  # 1 시세 제한
    if remainCount <= 0:
        print('시세 연속 조회 제한 회피를 위해 sleep', g_objCpStatus.LimitRequestRemainTime)
        time.sleep(g_objCpStatus.LimitRequestRemainTime / 1000)

###############################################################################
# 전일 대비 계산
def getStkVwap(stkTickData):
    sumAskVwap = stkTickData.ask_prc[0] * stkTickData.ask_qty[0] + \
                 stkTickData.ask_prc[1] * stkTickData.ask_qty[1] + \
                 stkTickData.ask_prc[2] * stkTickData.ask_qty[2] + \
                 stkTickData.ask_prc[3] * stkTickData.ask_qty[3] + \
                 stkTickData.ask_prc[4] * stkTickData.ask_qty[4] + \
                 stkTickData.ask_prc[5] * stkTickData.ask_qty[5] + \
                 stkTickData.ask_prc[6] * stkTickData.ask_qty[6] + \
                 stkTickData.ask_prc[7] * stkTickData.ask_qty[7] + \
                 stkTickData.ask_prc[8] * stkTickData.ask_qty[8] + \
                 stkTickData.ask_prc[9] * stkTickData.ask_qty[9]

    sumAsk = stkTickData.ask_qty[0] + \
             stkTickData.ask_qty[1] + \
             stkTickData.ask_qty[2] + \
             stkTickData.ask_qty[3] + \
             stkTickData.ask_qty[4] + \
             stkTickData.ask_qty[5] + \
             stkTickData.ask_qty[6] + \
             stkTickData.ask_qty[7] + \
             stkTickData.ask_qty[8] + \
             stkTickData.ask_qty[9]

    sumBidVwap = stkTickData.bid_prc[0] * stkTickData.bid_qty[0] + \
                 stkTickData.bid_prc[1] * stkTickData.bid_qty[1] + \
                 stkTickData.bid_prc[2] * stkTickData.bid_qty[2] + \
                 stkTickData.bid_prc[3] * stkTickData.bid_qty[3] + \
                 stkTickData.bid_prc[4] * stkTickData.bid_qty[4] + \
                 stkTickData.bid_prc[5] * stkTickData.bid_qty[5] + \
                 stkTickData.bid_prc[6] * stkTickData.bid_qty[6] + \
                 stkTickData.bid_prc[7] * stkTickData.bid_qty[7] + \
                 stkTickData.bid_prc[8] * stkTickData.bid_qty[8] + \
                 stkTickData.bid_prc[9] * stkTickData.bid_qty[9]

    sumBid = stkTickData.bid_qty[0] + \
             stkTickData.bid_qty[1] + \
             stkTickData.bid_qty[2] + \
             stkTickData.bid_qty[3] + \
             stkTickData.bid_qty[4] + \
             stkTickData.bid_qty[5] + \
             stkTickData.bid_qty[6] + \
             stkTickData.bid_qty[7] + \
             stkTickData.bid_qty[8] + \
             stkTickData.bid_qty[9]

    askVwap = 0
    bidVwap = 0
    midVwap = 0
    midPrc  = 0
    prc_diff= 0
    if sumAsk != 0 and sumBid != 0 and (stkTickData.ask_qty[0] + stkTickData.bid_qty[0]) != 0 :
        askVwap = round(sumAskVwap / sumAsk, 8)
        bidVwap = round(sumBidVwap / sumBid, 8)
        midVwap = round((askVwap + bidVwap) / 2, 8)
        midPrc  = (stkTickData.ask_prc[0] * stkTickData.ask_qty[0] + stkTickData.bid_prc[0] * stkTickData.bid_qty[0]) / (stkTickData.ask_qty[0] + stkTickData.bid_qty[0])
        prc_diff = round(midPrc - midVwap, 8)
        midPrc  = round(midPrc, 8)

    return askVwap, bidVwap, midVwap, midPrc, prc_diff

###############################################################################
# 전일 대비 계산
def getFutVwap(futTickData):
    sumAskVwap = futTickData.ask_prc[0] * futTickData.ask_qty[0] + \
                 futTickData.ask_prc[1] * futTickData.ask_qty[1] + \
                 futTickData.ask_prc[2] * futTickData.ask_qty[2] + \
                 futTickData.ask_prc[3] * futTickData.ask_qty[3] + \
                 futTickData.ask_prc[4] * futTickData.ask_qty[4]

    sumAsk = futTickData.ask_qty[0] + \
             futTickData.ask_qty[1] + \
             futTickData.ask_qty[2] + \
             futTickData.ask_qty[3] + \
             futTickData.ask_qty[4]

    sumBidVwap = futTickData.bid_prc[0] * futTickData.bid_qty[0] + \
                 futTickData.bid_prc[1] * futTickData.bid_qty[1] + \
                 futTickData.bid_prc[2] * futTickData.bid_qty[2] + \
                 futTickData.bid_prc[3] * futTickData.bid_qty[3] + \
                 futTickData.bid_prc[4] * futTickData.bid_qty[4]

    sumBid = futTickData.bid_qty[0] + \
             futTickData.bid_qty[1] + \
             futTickData.bid_qty[2] + \
             futTickData.bid_qty[3] + \
             futTickData.bid_qty[4]

    askVwap = 0
    bidVwap = 0
    midVwap = 0
    midPrc = 0
    prc_diff = 0
    if sumAsk != 0 and sumBid != 0 and (futTickData.ask_qty[0] + futTickData.bid_qty[0]) != 0:
        askVwap = round(sumAskVwap / sumAsk, 8)
        bidVwap = round(sumBidVwap / sumBid, 8)
        midVwap = round((askVwap + bidVwap) / 2, 8)
        midPrc = (futTickData.ask_prc[0] * futTickData.ask_qty[0] + futTickData.bid_prc[0] * futTickData.bid_qty[0]) / (futTickData.ask_qty[0] + futTickData.bid_qty[0])
        prc_diff = round(midPrc - midVwap, 8)
        midPrc = round(midPrc, 8)

    return askVwap, bidVwap, midVwap, midPrc, prc_diff
        
###############################################################################
# 전일 대비 계산
def makediffp(self):
    lastday = 0
    if (self.exFlag == ord('1')):  # 동시호가 시간 (예상체결)
        if self.baseprice > 0:
            lastday = self.baseprice
        else:
            lastday = self.expcur - self.expdiff
        if lastday:
            self.expdiffp = (self.expdiff / lastday) * 100
        else:
            self.expdiffp = 0
    else:
        if self.baseprice > 0:
            lastday = self.baseprice
        else:
            lastday = self.cur - self.diff
        if lastday:
            self.diffp = (self.diff / lastday) * 100
        else:
            self.diffp = 0

def getCurColor(self):
    diff = self.diff
    if (self.exFlag == ord('1')):  # 동시호가 시간 (예상체결)
        diff = self.expdiff
    if (diff > 0):
        return 'color: red'
    elif (diff == 0):
        return 'color: black'
    elif (diff < 0):
        return 'color: blue'

###############################################################################
# PLUS 실행 기본 체크 함수
def InitPlusCheck():
    # 프로세스가 관리자 권한으로 실행 여부
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('정상: 관리자권한으로 실행된 프로세스입니다.')
    else:
        print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        return False
 
    # 연결 여부 체크
    if (g_objCpStatus.IsConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        return False
 
    return True

def InitTradeInit():
    # 주문 관련 초기화
    if (g_objCpTrade.TradeInit(0) != 0):
        print("주문 초기화 실패")
        return False

###############################################################################
#   time
dtime = datetime.datetime.now()
dtymd = dtime.strftime("%Y%m%d")


class FileMng:
    """
    파일 읽기 쓰기를 관리하는 클래스
    """

    @classmethod
    def write_file(cls, file_path, string):
        """
        파일에 문자열을 기록
        :param file_path: 저장할 파일의 경로 (str)
        :param string: 저장할 내용 (str)
        :return: 성공여부 (bool)
        """
        try:
            with open(file_path, "w") as f:
                f.write(string)
        except Exception as e:
            logging.error(e)
            return False

        return True

    @classmethod
    def read_file(cls, file_path):
        """
        파일에서 문자열을 읽어옴
        :param file_path: 저장할 파일의 경로 (str)
        :return: 성공시 불러온 내용 (str) / 실패시 None
        """
        ret = None

        if file_path is None:
            return None

        if not os.path.exists(file_path):
            logging.error("파일읽기 실패(파일없음), 상대경로: {0}, 절대경로: {1}".format(file_path, os.path.abspath(file_path)))
            return None

        try:
            with open(file_path, "r") as f:
                ret = f.read()
        except Exception as e:
            logging.error(e)

        return ret

class Aes256Cipher:
    """
    AES256 암/복호화 클래스
    """
    @classmethod
    def gen_key(cls):
        """
        무작위로 AesKey를 생성한다.
        :return: Base64로 인코딩된 암호화키 (str)
        """
        rand_val = Random.new().read(AES.key_size[-1])
        temp = hashlib.sha256(rand_val).digest()
        temp = base64.b64encode(temp).decode("ascii")
        return temp

    def encrypt_dict(self, dict_obj, key, charset="utf-8"):
        """
        Dictionary를 Aes256(CBC)로 암호화한다.
        :param dict_obj: 암호화할 대상 (dict)
        :param key: gen_key()로 생성된 암호화키 (str)
        :param charset: Character Set (str)
        :return: 성공시 Base64로 인코딩된 암호화값 (String) / 실패시 None
        """
        ret = None

        if type(dict_obj) is dict:
            try:
                json_text = json.dumps(dict_obj)
                ret = self.encrypt_str(json_text, key, charset)
            except Exception as e:
                logging.error(e)

        return ret

    @classmethod
    def encrypt_str(cls, plain_text, key, charset="utf-8"):
        """
        String을 Aes256(CBC)로 암호화한다.
        :param plain_text: 암호화할 대상 (str)
        :param key: gen_key()로 생성된 암호화키 (str)
        :param charset: Character Set (str)
        :return: 성공시 Base64로 인코딩된 암호화값 (str) / 실패시 None
        """
        cipher = None

        try:
            key = base64.b64decode(key.encode("ascii"))
            iv = Random.new().read(AES.block_size)
            temp = plain_text.encode(charset)
            temp = base64.b64encode(temp)
            temp = cls._padding(temp)
            encryptor = AES.new(key, AES.MODE_CBC, IV=iv)
            cipher = iv + encryptor.encrypt(temp)
            cipher = base64.b64encode(cipher).decode("ascii")
        except Exception as e:
            logging.error(e)

        return cipher

    def decrypt_dict(self, cipher, key, charset="utf-8"):
        """
        Aes256(CBC)로 복호화하여 Dictionary로 리턴한다.
        :param cipher: 복호화할 대상 (str)
        :param key: gen_key()로 생성된 암호화키 (str)
        :param charset: Character Set (str)
        :return: 성공시 복호화된 Dictionary (dict) / 실패시 None
        """
        ret = None

        try:
            plain_text = self.decrypt_str(cipher, key, charset)
            ret = json.loads(plain_text, encoding=charset)
        except Exception as e:
            logging.error(e)

        return ret

    @classmethod
    def decrypt_str(cls, cipher, key, charset="utf-8"):
        """
        Aes256(CBC)로 복호화하여 String으로 리턴한다.
        :param cipher: 복호화할 대상 (str)
        :param key: gen_key()로 생성된 암호화키 (str)
        :param charset: Character Set (str)
        :return: 성공시 복호화된 문자열 (str) / 실패시 None
        """
        plain = None

        try:
            cipher = base64.b64decode(cipher.encode("ascii"))
            key = base64.b64decode(key.encode("ascii"))
            iv = cipher[0:AES.block_size]
            cipher_body = cipher[AES.block_size:]

            encryptor = AES.new(key, AES.MODE_CBC, IV=iv)
            temp = encryptor.decrypt(cipher_body)
            temp = cls._unpadding(temp)
            temp = base64.b64decode(temp)
            plain = temp.decode(charset)
        except Exception as e:
            logging.error(e)

        return plain

    @classmethod
    def _padding(cls, plain):
        """
        Base64로 인코딩된 값에 Padding을 넣는다. (공백으로 채움)
        :param plain: 원본 (bytes)
        :return: Padding된 값 (bytes)
        """
        ret = plain

        if 0 != len(plain) % AES.block_size:
            length = AES.block_size - (len(plain) % AES.block_size)
            ret = plain + b' ' * length

        return ret

    @classmethod
    def _unpadding(cls, plain):
        """
        Base64로 인코딩된 값의 패딩을 지운다 (공백을 지움)
        :param plain: 원본 (bytes)
        :return: Unpadding된 값 (bytes)
        """
        return plain.decode("ascii").strip().encode("ascii")

###############################################################################
#   CreonPlusExecuter
class CreonPlusExecuter:
    """
    CybosPlus를 실행시키는 클래스
    사용자 정보와 암호화 키를 파일로부터 읽어오며,
    다른 방식으로 읽기를 원한다면 서브클래스를 만든뒤 get_user_info()를 오버라이딩 한다.
    """
    CP_PATH = "C:/CREON/STARTER/coStarter.exe"
    FILE_NAME_CP_LOGIN = "coStarter.exe"  # CP 로그인 프로세스명
    FILE_NAME_CP_RUN = "CpStart.exe"  # CP 공통모듈 프로세스명

    PYTHON32 = "H:/05.python/Anaconda3-5.2.0-Windows-x86/python.exe"
    CP_DATA_ITEM ="H:/05.python/Anaconda3-5.2.0-Windows-x86/python.exe H:/04.creon/02.zxTrader/creon_cpdata_main.py"
    CP_DATA_IDX  ="H:/05.python/Anaconda3-5.2.0-Windows-x86/python.exe H:/04.creon/02.zxTrader/creon_cpdatafut_main.py"

    def __init__(self):
        self.cipher_path = None
        self.key_path = None

    def execute_cp(self, user_info, cp_path=CP_PATH):
        """
        CybosPlus를 실행한다.
        :param user_info: CreonPlus 사용자정보, (dict, {id="아이디", pw="비밀번호", cert_pw="공인인증서 비밀번호"})
        :param cp_path: CybosPlus의 경로 (string)
        :return: 성공여부 (bool)
        """
        # CybosPlus가 이미 실행중인지 확인한다.
        proc_list = self._get_process_list()


        if self.FILE_NAME_CP_RUN in proc_list:
            print("CybosPlus 공통모듈이 이미 실행중 입니다. (프로세스명: CpStart.exe)")
            # 작동 되지 않음
            #os.system("taskkill /f /im CpStart.exe")
            g_objCpUtil.PlusDisconnect()
            time.sleep(5)
            proc_list = self._get_process_list()

        if self.FILE_NAME_CP_LOGIN in proc_list:
            while True:
                proc_list = self._get_process_list()

                if self.FILE_NAME_CP_LOGIN not in proc_list:
                    break

                logging.info("CybosPlus 로그인 창이 이미 실행 중 입니다. 공통모듈이 실행될 때까지 대기합니다. (프로세스명: coStarter.exe)")
                time.sleep(5)

            while True:
                proc_list = self._get_process_list()

                if self.FILE_NAME_CP_RUN in proc_list:
                    break

                print("CybosPlus 공통모듈이 실행될 때까지 대기합니다. (프로세스명: CpStart.exe)")
                time.sleep(5)

            print("CybosPlus 공통모듈이 실행되었습니다. (프로세스명: CpStart.exe)")
            return True

        # elif self.FILE_NAME_CP_RUN in proc_list:
        #     print("CybosPlus 공통모듈이 이미 실행중 입니다. (프로세스명: CpStart.exe)")
        #     os.system("taskkill /im CpStart.exe")
        #     g_objCpUtil.PlusDisconnect()
        #     return True

        is_success = False

        try:
            if user_info is None:
                return False

            # CybosPlus 실행
            path = "{0} /prj:cp /id:{1} /pwd:{2} /pwdcert:{3} /autostart".format(
                cp_path,
                user_info["id"],
                user_info["pw"],
                user_info["cert_pw"]
            )

            ret = os.system(path)
            if 0 == ret:
                is_success = True
                print("CybosPlus 공통모듈이 실행되었습니다. (프로세스명: CpStart.exe)")

            time.sleep(5)

            ret = os.system( "start H:/05.python/Anaconda3-5.2.0-Windows-x86/python.exe H:/04.creon/02.zxTrader/creon_cpdata_main.py %1")

            if 0 == ret:
                is_success = True
                print("CybosPlus 공통모듈이 실행되었습니다. (프로세스명: creon_cpdata_main)")

            time.sleep(5)

            ret = os.system("start H:/05.python/Anaconda3-5.2.0-Windows-x86/python.exe H:/04.creon/02.zxTrader/creon_cpdatafut_main.py %1")
            if 0 == ret:
                is_success = True
                print("CybosPlus 공통모듈이 실행되었습니다. (프로세스명: creon_cpdatafut_main)")

        except Exception as e:
            print(e)
            is_success = False

        return is_success

    def set_file_path(self, cipher_path, key_path):
        """
        암호화된 파일과 키 파일의 경로를 설정한다.
        :param cipher_path: 암호화된 파일의 경로
        :param key_path: 키 파일의 경로
        :return:
        """
        self.cipher_path = cipher_path
        self.key_path = key_path

    def get_user_info(self):
        """
        사용자 정보를 불러온다.
        다른 방식으로 사용자 정보를 불러오고 싶을땐 서브클래스에서 이 메소드만 오버라이딩하면 된다.
        :return: 성공시 {"id": 아이디, "pw": 비밀번호, "cert_pw": 공인인증서 비밀번호} (dict) / 실패시 None
        """
        # 암호화된 사용자 정보와 암호화키 파일을 읽는다.
        file_mng = FileMng()
        cipher_body = file_mng.read_file(self.cipher_path)
        aes_key = file_mng.read_file(self.key_path)

        if cipher_body is None or aes_key is None:
            return None

        # 사용자정보 복호화
        aes_cipher = Aes256Cipher()
        user_info = aes_cipher.decrypt_dict(cipher_body, aes_key)

        return user_info

    @classmethod
    def _get_process_list(cls):
        """
        윈도우에서 떠있는 프로세스 리스트를 가져온다
        :return: 프로세스명 리스트 (list)
        """
        ret = []
        wmi = win32com.client.GetObject('winmgmts:')
        processes = wmi.instancesOf('Win32_Process')

        for process in processes:
            ret.append(process.Properties_('Name').Value)

        return ret
