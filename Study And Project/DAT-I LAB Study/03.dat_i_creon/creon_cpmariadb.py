import sys
from PyQt5.QtWidgets import *
import win32com.client
from enum import Enum
from time import sleep
import threading
import pythoncom

import asyncio
import os
import pandas as pd

import time
import datetime
import pymysql
from configparser import ConfigParser
import logging
from util.utilities_logic import LoggerAdapter
# database define
from string_def import *

class CpDB:
    def __init__(self):
        super().__init__()
        self.ts = time.time()
        self.ymd = datetime.datetime.fromtimestamp(self.ts).strftime('%Y%m%d')
        self.timestamp = datetime.datetime.fromtimestamp(self.ts).strftime('%Y-%m-%d %H:%M:%S.%f')

        self.logger = logging.getLogger("my_setting")
        self.logger = LoggerAdapter(CpDB.__name__, self.logger)

        # db 정보 초기화
        config = ConfigParser()
        config.read('setting/init.ini')
        db = config['db']

        self.logger.debug(f'db: {db["USR"]} {db["URL"]} {int(db["PORT"])} {db["DB"]}')

        self.db_info = {
            DataBase.USR: db["USR"],
            DataBase.PWD: db["PW"],
            DataBase.URL: db["URL"],
            DataBase.PORT: int(db["PORT"]),
            DataBase.DB: db["DB"]
        }
        ###############################################################################
        #   Connect
        os.environ["NLS_LANG"] = ".AL32UTF8"
        hostname = os.environ['COMPUTERNAME']

        self.logger.debug(f'db: {self.db_info[DataBase.USR]}')

        # Open database connection
        self.con = pymysql.connect(host=self.db_info[DataBase.URL],
                                   port=self.db_info[DataBase.PORT],
                                   user=self.db_info[DataBase.USR],
                                   passwd=self.db_info[DataBase.PWD],
                                   db=self.db_info[DataBase.DB],
                                   charset='utf8', autocommit=False)

        # Connection 으로부터 Dictoionary Cursor 생성
        self.cur = self.con.cursor(pymysql.cursors.DictCursor)

    def connect(self):
        con = pymysql.connect(host=self.db_info[DataBase.URL],
                              port=self.db_info[DataBase.PORT],
                              user=self.db_info[DataBase.USR],
                              passwd=self.db_info[DataBase.PWD],
                              db=self.db_info[DataBase.DB],
                              charset='utf8', autocommit=False)

        return con
    
    def stkhistprc(self, icon, tp, idata):

        if  tp == 'I':

            print("*******************************************************")
            print("def STKHISTPRC(self, tp, idata, odata): ")
            print("*******************************************************")

            sql = """INSERT INTO TRD.STKHISTPRC
                     (YMD, ITEM, OPEN, HIGH, 
                      LOW, CLOSE, ACC_VOL, DIFF, 
                      item_nm                                    
                     )
                     VALUES
                     (%s, %s, %s, %s,
                      %s, %s, %s, %s,
                      %s
                      )
                 """
            cnt = len(idata.ymd)
            print("def STKHISTPRC(self, tp, idata, odata): > ", cnt, idata.ymd)
            
            idatam = []
            for i in range(cnt):
                idatam.append(
                   (idata.ymd[i], idata.item[i], idata.open[i], idata.high[i],
                    idata.low[i], idata.close[i], idata.acc_vol[i], idata.diff[i],
                    idata.item_nm[i])
                )
                
            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)

            except:
                icon.rollback()

            icon.commit()
            
            return
        
        if  tp == 'S':

            print("*******************************************************")
            print("def STKHISTPRC Select ")
            print("*******************************************************")

            sql = """SELECT YMD DATE, OPEN, HIGH, LOW, close, ACC_VOL VOLUME
                       FROM TRD.STKHISTPRC
                      WHERE YMD BETWEEN '20110714' AND '20110720'
                      ORDER BY YMD
                 """
            
            odata = pd.read_sql_query(sql, icon)
            print(odata)
            
            """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql)

                    # 데이타 Fetch
                    rows = self.cur.fetchall()
                    for date, open, high, low, close, volume in rows:

                        odata.ymd.append(date)
                        odata.open.append(open)
                        odata.high.append(high)
                        odata.low.append(low)
                        odata.close.append(close)
                        odata.acc_vol.append(volume)
            except:
                self.icon.rollback()

            self.icon.commit()
            """
            return odata
        
    def futchartdata(self, icon, tp, idata, odata):

        if  tp == 'I':

            print("*******************************************************")
            print("def futchartdata(self, icon, tp, idata, odata): ")
            print("*******************************************************")

            sql = """INSERT INTO TRD.FUTCHARTDATA
                     (YMD     , ITEM    , HHMM    , TM_TP   ,
                      OPEN    , HIGH    , LOW     , CLOSE   , ACC_VOL                
                     )
                     VALUES
                     (%s, %s, %s, %s,   
                      %s, %s, %s, %s, %s
                      )
                 """

            cnt = len(idata.ymd)
            print("def futchartdata(self, icon, tp, idata, odata): > ", cnt)

            idatam = []

            for i in range(cnt):
                idatam.append(
                   (idata.ymd[i],  idata.item[i], idata.hhmm[i], idata.tm_tp[i],
                    idata.open[i], idata.high[i], idata.low[i], idata.close[i], idata.acc_vol[i]
                    )
                )

            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)


            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                icon.rollback()

            icon.commit()

    def tivtt(self, icon, tp, idata, odata):

        if  tp == 'I':

            print("*******************************************************")
            print("def tivtt(self, tp, idata, odata): ")
            print("*******************************************************")

            sql = """INSERT INTO TRD.TIVTT
                     (MKT_TP       , MKT_NM       , IVT_TP       , IVT_NM       , TIME         ,
                      ASK_QTY      , ASK_AMT      , BID_QTY      , BID_AMT      ,
                      NET_BID_QTY  , NET_BID_AMT                         
                     )
                     VALUES
                     (%s, %s, %s, %s, %s,   
                      %s, %s, %s, %s, 
                      %s, %s
                      )
                 """

            cnt = len(idata.mkt_tp)
            print("def tivtt(self, tp, idata, odata): > ", cnt)

            idatam = []

            for i in range(cnt):
                idatam.append(
                   (idata.mkt_tp[i], idata.mkt_nm[i], idata.ivt_tp[i], idata.ivt_nm[i], idata.time[i],
                    idata.ask_qty[i], idata.ask_amt[i], idata.bid_qty[i], idata.bid_amt[i],
                    idata.net_bid_qty[i], idata.net_bid_amt[i]
                    )
                )

            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)


            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                icon.rollback()

            icon.commit()

    def stkindt(self, tp, idata, odata):

        if  tp == 'I':

            print("*******************************************************")
            print("def stkindt(self, tp, idata, odata): ")
            print("*******************************************************")

            sql = """INSERT INTO TRD.STKINDT
                     (YMD         , TP       , TERM    , ITEM  , 
                      MA5         , MA10     , MA20    , MA60  , MA120 , MA240 , 
                      VOL_AVG     , VOL_STD                       
                     )
                     VALUES
                     (%s, %s, %s, %s,  
                      %s, %s, %s, %s, %s, %s,
                      %s, %s
                      )
                 """
            cnt = len(idata.ymd)
            print("def stkindt(self, tp, idata, odata): > ", cnt, idata.ymd)

            idatam = []
            idatam.append(
               (idata.ymd, idata.tp, idata.term, idata.item,
                idata.ma5, idata.ma10, idata.ma20, idata.ma60, idata.ma120, idata.ma240,
                idata.vol_avg, idata.vol_std
                )
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)


            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

    def stkidxmst(self, tp, icon, idata, odata):

        if tp == 'S':

            sql = """SELECT ITEM
                       FROM TRD.STKIDXMST
                  """
            try:
                with icon.cursor() as cur:
                    cur.execute(sql)

                    odata.item = []
                    # 데이타 Fetch
                    rows = cur.fetchall()
                    for item in rows:
                        odata.item.append(item)

            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                icon.rollback()

            icon.commit()

        if  tp == 'I':

            print("*******************************************************")
            print("def stkidxmst(self, tp, icon, idata, odata): ", idata.item, idata.item_nm)
            print("*******************************************************")

            sql = """INSERT INTO TRD.STKIDXMST
                     (ITEM  , ITEM_NM                    
                     )
                     VALUES
                     (%s, %s
                      )
                 """
            idatam = []
            idatam.append(
               (idata.item,  idata.item_nm
                )
            )

            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)

            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                icon.rollback()

            icon.commit()

        return

    def stkidxd(self, tp, icon, idata, odata):

        if  tp == 'I':

            cnt = len(idata.ymd)
            print("*******************************************************")
            print("def stkidxd(self, tp, idata, odata): ", idata.ymd, idata.item, idata.item_nm)
            print("*******************************************************")

            sql = """INSERT INTO TRD.STKIDXD
                     (YMD         , ITEM  , ITEM_NM  , 
                      BF_CLOSE    , CLOSE , DIFF     , OPEN  , HIGH    , LOW  ,  
                      ACC_VOL                            
                     )
                     VALUES
                     (%s, %s, %s,   
                      %s, %s, %s, %s, %s, %s,
                      %s
                      )
                 """
            idatam = []
            idatam.append(
               (idata.ymd,      idata.item,  idata.item_nm,
                idata.bf_close, idata.close, idata.diff, idata.open, idata.high, idata.low,
                idata.acc_vol
                )
            )

            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)

            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                icon.rollback()

            icon.commit()

            print("icon.commit()", cur.lastrowid)

        return

    def stkidxt(self, tp, icon, idata, odata):

        if  tp == 'I':

            print("*******************************************************")
            print("def stkidxt(self, tp, idata, odata): ")
            print("*******************************************************")

            sql = """INSERT INTO TRD.STKIDXT
                     (YMD         , ITEM  , ITEM_NM  , 
                      BF_CLOSE    , CLOSE , DIFF     , OPEN  , HIGH    , LOW  ,  
                      ACC_VOL, TIME                           
                     )
                     VALUES
                     (%s, %s, %s,   
                      %s, %s, %s, %s, %s, %s,
                      %s, %s
                      )
                 """
            cnt = len(idata.ymd)
            print("def stkindt(self, tp, idata, odata): > ", cnt, idata.ymd)

            idatam = []
            idatam.append(
               (idata.ymd,      idata.item,  idata.item_nm,
                idata.bf_close, idata.close, idata.diff, idata.open, idata.high, idata.low,
                idata.acc_vol,  idata.time
                )
            )

            # Open database connection
            #con = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='MySql', charset='utf8', autocommit=False)
            # Connection 으로부터 Dictoionary Cursor 생성
            #cur = con.cursor(pymysql.cursors.DictCursor)

            try:
                with icon.cursor() as cur:
                    cur.executemany(sql, idatam)


            except icon.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                icon.rollback()
                return

        icon.commit()
        return

    def stkodr(self, tp, idata, odata):

        if  tp == 'I':

            sql = """INSERT INTO TRD.STKODR
                     (YMD              ,ACC_NO           , ITEM             , 
                      ODR_NO           ,QTY              , PRC              , 
                      ODR_TP           ,COND_TP          , ODR_TICK_TP                     
                     )
                     VALUES
                     (%s, %s, %s,  
                      %s, %s, %s, 
                      %s, %s, %s
                      )
                 """
            cnt = len(idata.ymd)
            print("def stkodr(self, tp, idata, odata): > ", cnt, idata.ymd)

            idatam = []
            idatam.append(
               (idata.ymd,
                idata.acc_no,
                idata.item,
                idata.odr_no, idata.qty, idata.prc,
                idata.odr_tp, idata.cond_tp, idata.odr_tick_tp)
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except:
                self.con.rollback()

            self.con.commit()

        if  tp == 'U':

            sql = """UPDATE TRD.STKODR
                        SET CON_QTY    = %s
                          , CON_PRC    = %s
                      WHERE YMD        = %s
                        AND ITEM       = %s
                        AND ACC_NO     = %s
                        AND ODR_NO     = %s
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (idata.con_qty, idata.con_prc,
                                      idata.ymd, idata.item, idata.acc_no, idata.odr_no
                                      ))

            except:
                self.con.rollback()

            self.con.commit()

    def stkcurt(self, tp, idata, odata):

        if  tp == 'I':

            sql = """INSERT INTO TRD.STKCURT
                     (YMD              ,ITEM             , 
                      OPEN             ,HIGH             , LOW              , 
                      CLOSE            ,DIFF             , VOL              ,
                      ACC_VOL          ,AMT              , ODR_TP           ,
                      PRC_SIGN         ,
                      TIME             , TIMES                                                    
                     )
                     VALUES
                     (%s, %s,   
                      %s, %s, %s, 
                      %s, %s, %s,
                      %s, %s, %s,
                      %s,
                      %s, %s
                      )
                """

            print("def stkcurt(self, tp, idata, odata):", idata.ymd, idata.item, idata.close, idata.odr_tp)

            idatam = []
            idatam.append(
                (idata.ymd, idata.item,
                idata.open, idata.high, idata.low,
                idata.close, idata.diff, idata.vol,
                idata.acc_vol, idata.amt, idata.odr_tp,
                idata.prc_sign,
                idata.time, idata.times)
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                os._exit(1)
                self.con.rollback()

            self.con.commit()

            print(self.cur.lastrowid)

        return

    def stktick(self, tp, idata, odata):

        if  tp == 'I':

            sql = """INSERT INTO TRD.STKTICK
                     (YMD           , ITEM          , ITEM_NM       ,
                      TIME          , ACC_VOL       ,
                      ASK_QTY10     , ASK_QTY9      , ASK_QTY8      , ASK_QTY7      , ASK_QTY6      ,
                      ASK_QTY5      , ASK_QTY4      , ASK_QTY3      , ASK_QTY2      , ASK_QTY1      ,
                      ASK_PRC10     , ASK_PRC9      , ASK_PRC8      , ASK_PRC7      , ASK_PRC6      ,
                      ASK_PRC5      , ASK_PRC4      , ASK_PRC3      , ASK_PRC2      , ASK_PRC1      ,
                      BID_QTY10     , BID_QTY9      , BID_QTY8      , BID_QTY7      , BID_QTY6      ,
                      BID_QTY5      , BID_QTY4      , BID_QTY3      , BID_QTY2      , BID_QTY1      ,
                      BID_PRC10     , BID_PRC9      , BID_PRC8      , BID_PRC7      , BID_PRC6      ,
                      BID_PRC5      , BID_PRC4      , BID_PRC3      , BID_PRC2      , BID_PRC1      ,
                      ASK_TOT_QTY   , BID_TOT_QTY   , EXTIME_ASK_TOT_QTY, EXTIME_BID_TOT_QTY        ,
                      ASK_VWAP      , BID_VWAP      , MID_VWAP      , MID_PRC       , PRC_DIFF      
                     )
                     VALUES
                     (%s, %s, %s,   
                      %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s,
                      %s, %s, %s, %s, %s
                      )
                """
            idatam = []
            idatam.append(
               (idata.ymd, idata.item, idata.item_nm,
                idata.time, idata.acc_vol,
                idata.ask_qty[9], idata.ask_qty[8], idata.ask_qty[7], idata.ask_qty[6], idata.ask_qty[5],
                idata.ask_qty[4], idata.ask_qty[3], idata.ask_qty[2], idata.ask_qty[1], idata.ask_qty[0],
                idata.ask_prc[9], idata.ask_prc[8], idata.ask_prc[7], idata.ask_prc[6], idata.ask_prc[5],
                idata.ask_prc[4], idata.ask_prc[3], idata.ask_prc[2], idata.ask_prc[1], idata.ask_prc[0],
                idata.bid_qty[9], idata.bid_qty[8], idata.bid_qty[7], idata.bid_qty[6], idata.bid_qty[5],
                idata.bid_qty[4], idata.bid_qty[3], idata.bid_qty[2], idata.bid_qty[1], idata.bid_qty[0],
                idata.bid_prc[9], idata.bid_prc[8], idata.bid_prc[7], idata.bid_prc[6], idata.bid_prc[5],
                idata.bid_prc[4], idata.bid_prc[3], idata.bid_prc[2], idata.bid_prc[1], idata.bid_prc[0],
                idata.ask_tot_qty, idata.bid_tot_qty, idata.extime_ask_tot_qty, idata.extime_bid_tot_qty,
                idata.ask_vwap, idata.bid_vwap, idata.mid_vwap, idata.mid_prc, idata.prc_diff
                )
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        return

    def futtick(self, tp, idata, odata):

        if  tp == 'I':

            sql = """INSERT INTO TRD.FUTTICK
                     (YMD           , ITEM          , ITEM_NM       ,
                      TIME          , ACC_VOL       ,
                      ASK_NUM5      , ASK_NUM4      , ASK_NUM3      , ASK_NUM2      , ASK_NUM1      ,
                      ASK_QTY5      , ASK_QTY4      , ASK_QTY3      , ASK_QTY2      , ASK_QTY1      ,
                      ASK_PRC5      , ASK_PRC4      , ASK_PRC3      , ASK_PRC2      , ASK_PRC1      ,
                      BID_PRC5      , BID_PRC4      , BID_PRC3      , BID_PRC2      , BID_PRC1      ,
                      BID_QTY5      , BID_QTY4      , BID_QTY3      , BID_QTY2      , BID_QTY1      ,
                      BID_NUM5      , BID_NUM4      , BID_NUM3      , BID_NUM2      , BID_NUM1      ,
                      ASK_TOT_NUM   , ASK_TOT_QTY   , BID_TOT_NUM   , BID_TOT_QTY   , MKT_STAT_TP   ,
                      ASK_VWAP      , BID_VWAP      , MID_VWAP      , MID_PRC       , PRC_DIFF      
                     )
                     VALUES
                     (%s, %s, %s,   
                      %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s
                      )
                """
            idatam = []
            idatam.append(
               (idata.ymd, idata.item, idata.item_nm,
                idata.time, idata.acc_vol,
                idata.ask_num[4], idata.ask_num[3], idata.ask_num[2], idata.ask_num[1], idata.ask_num[0],
                idata.ask_qty[4], idata.ask_qty[3], idata.ask_qty[2], idata.ask_qty[1], idata.ask_qty[0],
                idata.ask_prc[4], idata.ask_prc[3], idata.ask_prc[2], idata.ask_prc[1], idata.ask_prc[0],
                idata.bid_prc[4], idata.bid_prc[3], idata.bid_prc[2], idata.bid_prc[1], idata.bid_prc[0],
                idata.bid_qty[4], idata.bid_qty[3], idata.bid_qty[2], idata.bid_qty[1], idata.bid_qty[0],
                idata.bid_num[4], idata.bid_num[3], idata.bid_num[2], idata.bid_num[1], idata.bid_num[0],
                idata.ask_tot_num, idata.ask_tot_qty, idata.bid_tot_qty, idata.bid_tot_num, idata.mkt_stat_tp,
                idata.ask_vwap, idata.bid_vwap, idata.mid_vwap, idata.mid_prc, idata.prc_diff
                )
            )

            print("def futtick(self, tp, idata, odata):", idata.ymd, idata.item, idata.ask_vwap, idata.bid_vwap, idata.mid_vwap, idata.mid_prc, idata.prc_diff)

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        return

    def futcurt(self, tp, idata, odata):

        if  tp == 'I':

            sql = """INSERT INTO TRD.FUTCURT
                     (YMD              ,ITEM             , 
                      OPEN             ,HIGH             , LOW              , 
                      CLOSE            ,DIFF             , 
                      ACC_VOL          , 
                      PRC_SIGN         ,
                      TIME             ,
                      K200_IDX         ,
                      OPEN_INTEREST    , FST_OFFER_PRC    , FST_BID_PRC      , FST_OFFER_VOL    , FST_BID_VOL      ,
                      ACC_OFFER_VOL    , ACC_BID_VOL      
                     )
                     VALUES
                     (%s, %s,   
                      %s, %s, %s, 
                      %s, %s, 
                      %s,  
                      %s,
                      %s,
                      %s, 
                      %s, %s, %s, %s, %s, 
                      %s, %s
                      )
                """

            print("def futcurt(self, tp, idata, odata):", idata.ymd, idata.item, idata.close)

            idatam = []
            idatam.append(
                (idata.ymd, idata.item,
                idata.open, idata.high, idata.low,
                idata.close, idata.diff,
                idata.acc_vol,
                idata.prc_sign,
                idata.time,
                idata.k200_idx,
                idata.open_interest,idata.fst_offer_prc,
                idata.fst_bid_prc,
                idata.fst_offer_vol,
                idata.fst_bid_vol,
                idata.acc_offer_vol,
                idata.acc_bid_vol
                )
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}", error)
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        return

    def stkmst(self, tp, idata, odata):

        print("def stkmst(self, tp, idata, odata):", tp)

        if  tp == 'I':
            sql = """DELETE FROM TRD.STKMST
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql)


            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")
                self.con.rollback()
                return

            sql = """INSERT INTO TRD.STKMST
                     (ITEM, ITEM_NM, STK_TP, BASE_ITEM, BASE_ITEM_NM
                      )
                     VALUES
                     (%s, %s, %s, %s, %s
                      )
                    """
            cnt = len(idata.item)

            print("def stkmst(self, tp, idata, odata):", cnt)

            idatam = []
            for i in range(cnt):
                idatam.append(
                    (idata.item[i],idata.item_nm[i], idata.stk_tp[i], idata.base_item[i], idata.base_item_nm[i])
                )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)


            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")
                self.con.rollback()
                return

            self.con.commit()

    def stkblnc(self, tp, idata, odata):

        cnt = len(idata.acc_no)
        for i in range(cnt) :
            print("STKBLNC idata.ymd", self.ymd, idata.acc_no[i], idata.item[i], idata.con_qty[i], idata.td_qty[i], idata.con_prc[i], idata.val_amt[i])

        if  tp == 'I':
            sql = """DELETE FROM TRD.STKBLNC 
                      WHERE YMD = %s
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (self.ymd))
            except:
                self.con.rollback()
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")
                return

            sql = """INSERT INTO TRD.STKBLNC
                     (ACC_NO, ITEM, ITEM_NM, 
                      CON_QTY, CON_PRC, TD_QTY, YD_QTY, 
                      VAL_AMT, PL_AMT 
                      )
                     VALUES
                     (%s, %s, %s,
                      %s, %s, %s, %s, 
                      %s, %s
                      )
                    """
            cnt = len(idata.acc_no)

            idatam = []
            for i in range(cnt):
                idatam.append(
                    (idata.acc_no[i] , idata.item[i], idata.item_nm[i],
                     idata.con_qty[i], idata.con_prc[i], idata.td_qty[i], idata.yd_qty[i],
                     idata.val_amt[i], idata.pl_amt[i])
                )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, idatam)

            except:
                self.con.rollback()
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")
                return

            self.con.commit()

        if tp == 'S':

            sql = """SELECT ACC_NO, ITEM, ITEM_NM, QTY, TD_QTY, YD_QTY, CON_PRC, AMT, VAL_AMT, PL_AMT  
                       FROM TRD.STKBLNC 
                      ORDER BY ITEM
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql)

                    # 데이타 Fetch
                    rows = self.cur.fetchall()
                    for acc_no, item, item_nm, qty, td_qty, yd_qty, con_prc, amt, val_amt, pl_amt in rows:

                        odata.acc_no.append(acc_no)
                        odata.item.append(item)
                        odata.item_nm.append(item_nm)
                        odata.qty.append(qty)
                        odata.td_qty.append(td_qty)
                        odata.yd_qty.append(yd_qty)
                        odata.con_prc.append(con_prc)
                        odata.amt.append(amt)
                        odata.val_amt.append(val_amt)
                        odata.pl_amt.append(pl_amt)

            except:
                self.con.rollback()

            self.con.commit()
            return

    def stkcon(self, tp, idata, odata):

        if tp == 'S':

            sql = """SELECT YMD      ,RTIME    ,ACC_NO   ,STRTGY_NO,ITEM     ,   
                            ODR_NO   ,ORG_NO   ,CON_QTY  ,CON_PRC  ,ODR_TP   ,   
                            CON_TP   ,CNCL_TP  ,SHORT_QTY,BLNC_QTY ,ODR_QTY  ,   
                            ODR_NM   ,CON_NM  ,
                            ODR_PRC  ,ACC_NM   ,ITEM_NM  ,MTIME  
                       FROM TRD.STKCON WHERE YMD = %s 
                      ORDER BY RTIME DESC
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (self.ymd))

                    odata.ymd = []
                    odata.rtime = []
                    odata.acc_no = []
                    odata.strtgy_no = []
                    odata.item     = []
                    odata.odr_no = []
                    odata.org_no = []
                    odata.con_qty = []
                    odata.con_prc = []
                    odata.odr_tp = []
                    odata.con_tp = []
                    odata.cncl_tp = []
                    odata.short_qty = []
                    odata.blnc_qty = []
                    odata.odr_qty = []
                    odata.odr_prc = []
                    odata.acc_nm = []
                    odata.item_nm = []
                    odata.mtime = []

                    # 데이타 Fetch
                    rows = self.cur.fetchall()
                    for ymd      ,rtime    ,acc_no   ,strtgy_no,item     , \
                        odr_no   ,org_no   ,con_qty  ,con_prc  ,odr_tp   , \
                        con_tp   ,cncl_tp  ,short_qty,blnc_qty ,odr_qty  , \
                        odr_prc  ,acc_nm   ,item_nm  ,mtime in rows:

                        odata.ymd.append(ymd)
                        odata.rtime.append(rtime)
                        odata.acc_no.append(acc_no)
                        odata.strtgy_no.append(strtgy_no)
                        odata.item.append(item)
                        odata.odr_no.append(odr_no)
                        odata.org_no.append(org_no)
                        odata.con_qty.append(con_qty)
                        odata.con_prc.append(con_prc)
                        odata.odr_tp.append(odr_tp)
                        odata.con_tp.append(con_tp)
                        odata.cncl_tp.append(cncl_tp)
                        odata.short_qty.append(short_qty)
                        odata.blnc_qty.append(blnc_qty)
                        odata.odr_qty.append(odr_qty)
                        odata.odr_prc.append(odr_prc)
                        odata.acc_nm.append(acc_nm)
                        odata.item_nm.append(item_nm)
                        odata.mtime.append(mtime)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

        if tp == 'I':

            print("STKCON idata.ymd", self.ymd)

            sql = """INSERT INTO TRD.STKCON
                     (YMD      ,ACC_NO   ,ITEM     ,
                      ODR_NO   ,ORG_NO   ,CON_QTY  ,CON_PRC  ,ODR_TP   ,
                      CON_TP   ,CNCL_TP  ,SHORT_QTY,BLNC_QTY ,ODR_QTY  ,
                      ODR_NM   , CON_NM
                      )
                     VALUES
                     (%s, %s,%s,
                      %s, %s,%s, %s, %s,
                      %s, %s,%s, %s, %s,
                      %s, %s
                      )
                """

            idatam = []
            idatam.append(
                (self.ymd       ,idata.acc_no   ,idata.item     ,
                 idata.odr_no   ,idata.org_no   ,idata.con_qty  ,idata.con_prc  ,idata.odr_tp   ,
                 idata.con_tp   ,idata.cncl_tp  ,idata.short_qty,idata.blnc_qty ,idata.odr_qty  ,
                 idata.odr_nm   ,idata.con_nm)
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, (idatam))

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

            # sql = """INSERT INTO TRD.STKCON
            #          (YMD      ,ACC_NO   ,ITEM     ,
            #           ODR_NO   ,ORG_NO   ,CON_QTY  ,CON_PRC  ,ODR_TP   ,
            #           CON_TP   ,CNCL_TP  ,SHORT_QTY,BLNC_QTY ,ODR_QTY  ,
            #           ODR_NM   , CON_NM
            #           )
            #          VALUES
            #          (%s, %s,%s,
            #           %s, %s,%s, %s, %s,
            #           %s, %s,%s, %s, %s,
            #           %s, %s
            #           )
            #     """
            # try:
            #     with con.cursor() as cur:
            #         cur.execute(sql, (idata.ymd      ,idata.acc_no   ,idata.item     ,
            #                           idata.odr_no   ,idata.org_no   ,idata.con_qty  ,idata.con_prc  ,idata.odr_tp   ,
            #                           idata.con_tp   ,idata.cncl_tp  ,idata.short_qty,idata.blnc_qty ,idata.odr_qty  ,
            #                           idata.odr_nm   ,idata.con_nm    ))
            #
            # except con.Error as error:
            #     print("*******************************************************")
            #     print("Error: {}".format(error))
            #     print("*******************************************************")
            #
            #     con.rollback()
            #
            # finally:
            #     con.commit()
            #     pass

        return

    def stkstrtgy(self, tp, idata, odata):

        if tp == 'I':

            sql = """INSERT INTO TRD.STKSTRTGY
                    (YMD, STRTGY_NO, ITEM, ODR_TP, QTY, 
                     PRC, MSG
                     )
                     VALUES
                    (%s, %s, %s, %s, %s,
                     %s, %s
                    )                           
                  """
            idatam = []
            idatam.append(
                (idata.ymd, idata.strtgy_no, idata.item, idata.odr_tp, idata.qty,
                 idata.prc, idata.stgy_msg
                 )
            )

            try:
                with self.con.cursor() as self.cur:
                    self.cur.executemany(sql, (idatam))

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        # 최초 주문 접수
        if tp == 'F':

            print("==============================================")
            print("def stkstrtgy(self, tp, idata, odata): tp ", tp, idata.exec_tp, idata.rslt_tp, idata.con_tp,idata.can_tp, idata.item)
            print("==============================================")

            sql = """UPDATE TRD.STKSTRTGY
                            SET EXEC_TP    = %s
                              , RSLT_TP    = %s
                              , CON_TP     = %s
                              , CAN_TP     = %s
                              , MSG        = %s
                              , ODR_NO     = %s
                          WHERE YMD        = %s
                            AND STRTGY_NO  = %s
                            AND item       = %s
                      """

            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (idata.exec_tp, idata.rslt_tp, idata.con_tp, idata.can_tp,
                                           idata.msg, idata.odr_no,
                                           idata.ymd, idata.strtgy_no, idata.item
                                           ))

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        if tp == 'U':

            print("==============================================")
            print("def stkstrtgy(self, tp, idata, odata): tp ", tp, idata.exec_tp, idata.rslt_tp, idata.con_tp, idata.can_tp, idata.item)
            print("==============================================")

            sql = """UPDATE TRD.STKSTRTGY
                        SET EXEC_TP    = %s
                          , RSLT_TP    = %s
                          , CON_TP     = %s
                          , CAN_TP     = %s
                          , MSG        = %s
                      WHERE YMD        = %s
                        AND STRTGY_NO  = %s
                        AND item       = %s
                        AND ODR_NO     = %s
                  """

            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (idata.exec_tp, idata.rslt_tp, idata.con_tp, idata.can_tp,
                                           idata.msg,
                                           idata.ymd, idata.strtgy_no, idata.item,
                                           idata.odr_no
                                          ))

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        if tp == 'S':

            sql = """SELECT YMD, STRTGY_NO, ITEM, ODR_TP, EXEC_TP, RSLT_TP, CON_TP, CAN_TP
                          , QTY, PRC, MSG 
                       FROM TRD.STKSTRTGY
                      WHERE YMD = %s
                        AND EXEC_TP = 'N'
                      ORDER BY SEQ 
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql, (self.ymd))

                    odata.ymd = []
                    odata.strtgy_no = []
                    odata.item = []
                    odata.odr_tp = []
                    odata.exec_tp = []
                    odata.rslt_tp = []
                    odata.con_tp = []
                    odata.can_tp = []
                    odata.qty = []
                    odata.prc = []
                    odata.msg = []

                    # 데이타 Fetch
                    rows = self.cur.fetchall()
                    for ymd, strtgy_no, item, odr_tp, exec_tp, rslt_tp, con_tp, can_tp, qty, prc, msg in rows:
                        odata.ymd.append(ymd)
                        odata.strtgy_no.append(strtgy_no)
                        odata.item.append(item)
                        odata.odr_tp.append(odr_tp)
                        odata.exec_tp.append(exec_tp)
                        odata.rslt_tp.append(rslt_tp)
                        odata.con_tp.append(con_tp)
                        odata.can_tp.append(can_tp)
                        odata.qty.append(qty)
                        odata.prc.append(prc)
                        odata.msg.append(msg)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        return

    def stkmsttgt(self, tp, idata, odata):

        print("==============================================")
        print("def stkmsttgt(self, tp, idata, odata): tp ", tp)
        print("==============================================")

        if tp == 'S':

            sql = """SELECT ITEM
                       FROM TRD.STKMSTTGT
                      WHERE USE_TP = '1'
                  """
            try:
                with self.con.cursor() as self.cur:
                    self.cur.execute(sql)

                    odata.item = []

                    # 데이타 Fetch
                    rows = self.cur.fetchall()
                    for item in rows:
                        odata.item.append(item)

            except self.con.Error as error:
                print("*******************************************************")
                print("Error: {}".format(error))
                print("*******************************************************")

                self.con.rollback()

            self.con.commit()

        return