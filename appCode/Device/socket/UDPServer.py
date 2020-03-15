import socket
import threading 
from appCode.Common.utility import log

class UDPServer:
    def __init__(self, iPort, iCallback):
        self.mServerAddress = ('localhost', int(iPort))
        self.mReceiveThread = None
        self.mCallback = iCallback
        self.mStarted = False
        self.mEndReceive = True

    def startServer(self):
        if True == self.mStarted:
            return
        log('starting server on {} port {}'.format(*self.mServerAddress))
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mSocket.settimeout(1)
        self.mSocket.bind(self.mServerAddress)
        self.mEndReceive = False    
        self.mReceiveThread =  threading.Thread(target=self.recv) 
        self.mReceiveThread.setDaemon(True)
        self.mReceiveThread.start()

    def stopServer(self):
        if False == self.mStarted:
            return
        self.mStarted = True
        log('stopping server on {} port {}'.format(*self.mServerAddress))
        self.mEndReceive = True
        if None != self.mReceiveThread:
            self.mReceiveThread.join(1) 
        self.mSocket.shutdown(socket.SHUT_RDWR)
        self.mSocket.close()

    def send(self, iMessage, iAddress):
        try:
            self.mSocket.sendto(iMessage, iAddress)
        except socket.timeout as e:
            return

    def recv(self):
        self.mStarted = True
        while False == self.mEndReceive:
            try:
                wSocketReceive = self.mSocket.recvfrom(4096)
                if 2 == len(wSocketReceive):
                    data, address = wSocketReceive
                    if None != self.mCallback:
                        wReply = self.mCallback(data, address)
                        if (None != wReply) and ("" != wReply):
                            self.send( wReply, address)
                        
            except socket.timeout as e:
                pass
            
