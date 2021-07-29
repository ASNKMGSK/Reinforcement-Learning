# -*- coding: utf-8 -*-
import json
import struct
import global_def as gd
from socket import *

class OrderPort:
    def __init__(self, ord_form):
        self.ord_form = ord_form
        self.pckt = ''
        self.socket_obj = self._conn_socket()

    def _conn_socket(self):
        if not isinstance(self.ord_form, tuple):
            raise TypeError(f'argument order should be tuple! shape (2,)')

        socket_obj = socket(AF_INET, SOCK_STREAM)
        socket_obj.connect(self.ord_form)
        
        return socket_obj
        
    def send_pckt(self, req_data):
        
        body = json.dumps(req_data, ensure_ascii=False).encode("utf-8")
        header = struct.pack("I", htonl(len(body)))
    
        try:
            self.socket_obj.sendall(header + body)
        except IOError as e:
            if e.errno == errno.EPIPE:
                self._conn_socket()
                self.socket_obj.sendall(header + body)
                
    def recv_pckt(self):
        header = self.socket_obj.recv(4, MSG_WAITALL)
        if header:
            body_len = struct.unpack("I", header)[0]
            body_len = ntohl(body_len)
            req_data = self.socket_obj.recv(body_len)
            req_data = json.loads(req_data.decode("utf-8"))

            msg = req_data.get(gd.KEY_NM_DATA)
            #print(msg[0], msg[1], msg[2])
        
        return msg
        
class TcpClient:
    
    def tcpClient(self, req_data):
        
        with socket(AF_INET, SOCK_STREAM) as s:
            s.connect((gd.HOST, gd.PORT))
    
            body = json.dumps(req_data, ensure_ascii=False).encode("utf-8")
            header = struct.pack("I", htonl(len(body)))
    
            # 내용의길이(4byte, int) + 내용(bytes)
            s.sendall(header + body)
            
        