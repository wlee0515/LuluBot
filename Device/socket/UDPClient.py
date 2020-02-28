import socket
import threading 

class UDPClient:
    def __init__(self, iAddress, iPort, iCallback):
        self.mServerAddress = (iAddress, int(iPort))
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mSocket.settimeout(1)
        self.mReceiveThread = None
        self.mCallback = iCallback
        self.mEndReceive = True
        
    def stopSocket(self):
        self.mEndReceive = True
        if None != self.mReceiveThread:
            self.mReceiveThread.join() 
        self.mSocket.shutdown(socket.SHUT_RDWR)
        self.mSocket.close()
      
    def send(self, iMessage):
        try:
            self.mSocket.sendto(iMessage.encode('utf8'), self.mServerAddress)
        except socket.timeout as e:
            return

        if None == self.mReceiveThread:
            self.mEndReceive = False    
            self.mReceiveThread =  threading.Thread(target=self.recv) 
            self.mReceiveThread.start()

    def recv(self):
        while False == self.mEndReceive:
            try:
                data, server = self.mSocket.recvfrom(4096)
                if None != self.mCallback :
                    self.mCallback(data)
            except socket.timeout as e:
                pass

