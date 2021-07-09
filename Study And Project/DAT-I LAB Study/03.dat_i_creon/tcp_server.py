# -*- coding: utf-8 -*-
import sys
import signal

import threading
import socket
import socketserver
import configparser
import struct
import json
import time
import datetime
import global_def as gd
from decimal import Decimal
from queue import Queue, Empty
from db_handler import DbHandler

from signal import signal, SIGINT, SIGTERM
from sys import exit

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.is_run = False

    # client recevie
    def _request_listener(self, req_queue: Queue):
        while self.is_run:
            try:
                header = self.request.recv(4, socket.MSG_WAITALL)

                if header:
                    body_len = struct.unpack("I", header)[0]
                    body_len = socket.ntohl(body_len)
                    req_data = self.request.recv(body_len, socket.MSG_WAITALL)
                    req_data = json.loads(req_data.decode("utf-8"))

                    req_gdata = req_data.get(gd.KEY_NM_DATA)
                    print(req_gdata[0], req_gdata[1], req_gdata[2])
                    
                    #req_queue.put(req_data)
                    
                    send_list = [ 'TRD', 
                                  req_gdata[0],
                                  '1',
                                  req_gdata[1]] 
                    
                    trd_data = {
                        gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
                        gd.KEY_NM_DATA: send_list
                    }       
                    body = json.dumps(trd_data, ensure_ascii=False).encode("utf-8")
                    header = struct.pack("I", socket.htonl(len(body)))
                    self.request.sendall(header+body)
            
                else:
                    break

            except Exception as e:
                self.is_run = False
                break

    @classmethod
    def json_default(cls, val: any):
        if isinstance(val, datetime.date):
            return val.strftime("%Y-%m-%d %H:%M:%S.%f")
        elif isinstance(val, Decimal):
            return float(val)
        raise TypeError("not JSON serializable")

    # database receive
    def _receive_listener(self, rcv_queue: Queue):
        while self.is_run:
            try:
                rcv_data = rcv_queue.get(True, 1)
                evt_type = rcv_data.get(gd.KEY_NM_EVT)

                if gd.EVT_TYPE_GET_KP200_FUT == evt_type:
                    rows = rcv_data.get(gd.KEY_NM_DATA)

                    for row in rows:
                        send_data = {
                            gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
                            gd.KEY_NM_DATA: row
                        }
                        body = json.dumps(send_data, ensure_ascii=False, default=self.json_default)
                        body = body.encode("utf-8")
                        header = struct.pack("I", socket.htonl(len(body)))

                        self.request.sendall(header + body)

                elif gd.EVT_TYPE_FIN == evt_type or gd.KEY_NM_MSG == evt_type:
                    body = json.dumps(rcv_data, ensure_ascii=False, default=self.json_default)
                    body = body.encode("utf-8")
                    header = struct.pack("I", socket.htonl(len(body)))

                    self.request.sendall(header + body)

            except Empty as em:
                pass
            except Exception as e:
                self.is_run = False
                break

    def handle(self):
        self.is_run = True

        req_queue = Queue()
        rcv_queue = Queue()

        config = configparser.ConfigParser()
        config.read("config.ini")

        db_host = config.get("DB", "HOST")
        db_port = int(config.get("DB", "PORT"))
        db_user = config.get("DB", "USER")
        db_pw = config.get("DB", "PASSWORD")
        db_name = config.get("DB", "DB_NAME")
        db_charset = config.get("DB", "CHAR_SET")

        #db_handler_thd = DbHandler(req_queue, rcv_queue, db_host, db_port, db_user, db_pw, db_name, db_charset)
        #db_handler_thd.start()

        req_thd = threading.Thread(target=self._request_listener, args=(req_queue,))
        req_thd.start()

        rcv_thd = threading.Thread(target=self._receive_listener, args=(rcv_queue,))
        rcv_thd.start()

        req_thd.join()
        rcv_thd.join()

        #db_handler_thd.is_run = False


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
    
class ServerExit(Exception):
    pass    

if __name__ == "__main__":
    HOST = ""
    PORT = 8765
    
    signal(SIGINT, handler)
    signal(SIGTERM, handler)
    
    try:
        svr = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        with svr:
            ip, port = svr.server_address
    
            server_thread = threading.Thread(target=svr.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_thread.join()
            
            svr.shutdown()
            
    except Exception as e:
        print("except Exception as e", e)
    except KeyboardInterrupt:
        print("except KeyboardInterrupt")
        svr.server_thread.join()
        
        
    


