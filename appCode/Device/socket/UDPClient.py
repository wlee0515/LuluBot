import socket
import threading 

class UDPClient:
    def __init__(self, iAddress, iPort, iCallback):
        self.mServerAddress = (iAddress, int(iPort))
        self.mSocket = None
        self.mReceiveThread = None
        self.mCallback = iCallback
        self.mEndReceive = True
        self.mRunning = False
        
    def stopSocket(self):
        if False == self.mRunning:
            return
        self.mRunning = False
        if None != self.mReceiveThread:
            self.mEndReceive = True
            self.mReceiveThread.join()
            self.mReceiveThread = None

    def send(self, iMessage):
        if None == self.mSocket:
            if None != self.mReceiveThread:
                self.mEndReceive = True
                self.mReceiveThread.join()
                self.mReceiveThread = None
            self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.mSocket.settimeout(1)

        try:
            self.mSocket.sendto(iMessage, self.mServerAddress)
        except socket.timeout as e:
            return

        if None == self.mReceiveThread:
            self.mEndReceive = False    
            self.mReceiveThread =  threading.Thread(target=self.recv) 
            self.mReceiveThread.start()

    def recv(self):
        self.mRunning = True
        while False == self.mEndReceive:
            try:
                wSocketReceive = self.mSocket.recvfrom(4096)
                if 2 == len(wSocketReceive):
                    data, server = wSocketReceive
                    if None != self.mCallback :
                        self.mCallback(data)
            except socket.timeout as e:
                pass
            except socket.error as e:
                break

        self.mRunning = False
        self.mSocket.shutdown(socket.SHUT_RDWR)
        self.mSocket.close()
        self.mSocket = None
        self.mEndReceive = True
