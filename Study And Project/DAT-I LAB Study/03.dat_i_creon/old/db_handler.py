# -*- coding: utf-8 -*-
import pymysql
import threading
import time
import global_def as gd
from queue import Queue, Empty


class DbHandler(threading.Thread):
    CONFIG_KEY_DB = "DB"

    def __init__(self, req_queue: Queue, rcv_queue: Queue, db_host: str, db_port: int, db_user: str, db_pw: str, db_name: str, db_char_set: str = "utf8"):
        threading.Thread.__init__(self)

        self._db_host = db_host
        self._db_port = db_port
        self._db_user = db_user
        self._db_pw = db_pw
        self._db_name = db_name
        self._db_char_set = db_char_set

        self.req_queue = req_queue
        self.rcv_queue = rcv_queue
        self.is_run = False

    def __del__(self):
        if self._db_conn is not None:
            self._db_conn.close()
            self._db_conn = None

    def db_connect(self) -> pymysql.connections.Connection:
        try:
            db_conn = pymysql.connect(
                host=self._db_host,
                port=self._db_port,
                user=self._db_user,
                passwd=self._db_pw,
                db=self._db_name,
                charset=self._db_char_set,
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print("DB연결실패")
            raise Exception

        return db_conn

    @classmethod
    def db_close(cls, db_conn: pymysql.connections.Connection) -> None:
        db_conn.close()

    def send_err_msg(self, msg: str) -> None:
        self.rcv_queue.put({
            gd.KEY_NM_EVT: gd.EVT_TYPE_ERR,
            gd.KEY_NM_MSG: msg
        })

    def run(self):
        self.is_run = True

        while self.is_run:
            try:
                req_dict = self.req_queue.get(True, 1)
                evt = req_dict.get(gd.KEY_NM_EVT)

                if gd.EVT_TYPE_GET_KP200_FUT == evt:
                    date = req_dict.get(gd.KEY_NM_DATE)

                    if date is None:
                        self.send_err_msg("invalid parameters")
                        continue

                    if self.get_kp200_fut(int(date)) is False:
                        self.send_err_msg("failed to get_kp200_fut()")
                else:
                    self.send_err_msg("undefined event type")

            except Empty as e:
                pass

            time.sleep(0.1)

    def get_kp200_fut(self, date: int) -> bool:
        db_conn = self.db_connect()
        curs = db_conn.cursor()

        query = f"SELECT COUNT(*) AS cnt FROM K200_FUT_LIMIT_ORD WHERE YMD = {date} AND ISIN_CODE = 'KR4101QC0001';"
        curs.execute(query)
        rs = curs.fetchone()

        k200_fut_limit_ord_len = rs.get("cnt", 0)
        chunk_size = 1000
        offset = 0

        while offset < k200_fut_limit_ord_len:
            query = f"SELECT * FROM K200_FUT_LIMIT_ORD WHERE YMD = {date} AND ISIN_CODE = 'KR4101QC0001' ORDER BY SEQ LIMIT {offset}, {chunk_size};"
            curs.execute(query)
            rs = curs.fetchall()

            self.rcv_queue.put({
                gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
                gd.KEY_NM_DATA: rs
            })

            offset = offset + chunk_size

        curs.close()

        self.db_close(db_conn)

        self.rcv_queue.put({
            gd.KEY_NM_EVT: gd.EVT_TYPE_FIN
        })

        return True
