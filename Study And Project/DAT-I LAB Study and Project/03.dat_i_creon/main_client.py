# -*- coding: utf-8 -*-
import socket
import json
import struct
import global_def as gd

class TcpClient:
    
    def tcpClient(self, req_data):
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((gd.HOST, gd.PORT))
    
            body = json.dumps(req_data, ensure_ascii=False).encode("utf-8")
            header = struct.pack("I", socket.htonl(len(body)))
    
            # 내용의길이(4byte, int) + 내용(bytes)
            s.sendall(header + body)
    
            while True:
                # 수신할 데이터의 길이
                rcv = s.recv(4, socket.MSG_WAITALL)
    
                if rcv:
                    # 수신할 데이터의 길이를 int로 변환
                    body_len = struct.unpack("I", rcv)[0]
                    body_len = socket.ntohl(body_len)
    
                    # 데이터의 길이만큼 읽음
                    body = s.recv(body_len, socket.MSG_WAITALL)
    
                    if body:
                        rcv_json = body.decode("utf-8")
                        rcv_dict = json.loads(rcv_json)
    
                        evt_type = rcv_dict.get(gd.KEY_NM_EVT)
    
                        if gd.EVT_TYPE_GET_KP200_FUT == evt_type:
                            print(rcv_dict.get(gd.KEY_NM_DATA))
                        elif gd.EVT_TYPE_ERR == evt_type:
                            print("에러발생", rcv_dict)
                        elif gd.EVT_TYPE_FIN == evt_type:
                            print("수신완료", rcv_dict)
                            break
                        else:
                            break
    
                    else:
                        break
    
                else:
                    break


if "__main__" == __name__:
    
    req_data = {
                gd.KEY_NM_EVT: gd.EVT_TYPE_GET_KP200_FUT,
                gd.KEY_NM_DATE: 20200924
                }
            
    objTcpClient = TcpClient()
    objTcpClient.tcpClient(req_data)
