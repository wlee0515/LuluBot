import os, time, threading
from Device.socket import UDPClient, UDPServer
from Common.utility import log

gRti_Server_Address = "localhost"
gRti_Server_Port = 9000
gRti_Participant_TimeOut = 5

if "RTI_SERVER_ADDRESS" in os.environ:
    gRti_Server_Address = os.environ["RTI_SERVER_ADDRESS"] 

if "RTI_SERVER_PORT" in os.environ:
    gRti_Server_Port = int(os.environ["RTI_SERVER_PORT"])

if "RTI_PARTICIPANT_TIMEOUT" in os.environ:
    gRti_Participant_TimeOut = float(os.environ["RTI_PARTICIPANT_TIMEOUT"])
    if gRti_Participant_TimeOut < 1.0:
        gRti_Participant_TimeOut = 1.0

log("RTI server address : {}:{}".format(gRti_Server_Address, gRti_Server_Port))


class Participant_Proxy:
    def __init__(self, iAddress):
        self.mAddress = iAddress
        self.mElapseTime = 0
        self.mSubscriptionList = {}

    def processMessage(self, iMessage):
        log(iMessage)
        return True

    def checkSubscription(self, iMessage):
        return True

class RTIProcess:
    def __init__(self):
        self.mUDPServer = UDPServer(gRti_Server_Port, self.message)
        self.mParticipantList = {}
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None
        self.mLastEntryPointTime = None


    def startServer(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mUDPServer.startServer()
        self.mEntryPointThread = threading.Thread(target=self.entryPoint) 
        self.mEntryPointThread.start()

    def stopServer(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        self.mUDPServer.stopServer()
        if None != self.mEntryPointThread:
            self.mRunning = False
            self.mEntryPointThread.join()
            self.mEntryPointThread = None
        self.mParticipantList.clear()

    def entryPoint(self):
        self.mRunning = True
        print("Entry point started with participant Timeout at {} s".format(gRti_Participant_TimeOut))
        wLastTime = time.time()

        while(self.mRunning):
            wCurrentTime = time.time()
            wDeltaTime = wCurrentTime - wLastTime
            wDeleteList = []
            for wKey, wProxy in self.mParticipantList.items():
                if wProxy.mElapseTime > gRti_Participant_TimeOut:
                    wDeleteList.append(wKey)
                else:            
                    wProxy.mElapseTime += wDeltaTime
                  
            
            for wItem in wDeleteList:
                wProxy = self.mParticipantList[wKey]
                wAddressString = "{}:{}".format(*wProxy.mAddress)
                log("Participant {} left".format(wAddressString))
                del self.mParticipantList[wKey]

            wLastTime = wCurrentTime
            time.sleep((gRti_Participant_TimeOut+1)/10)

        print("Entry point Exited")


    def message(self, iMessage, iAddress):
        wAddressString = "{}:{}".format(*iAddress)
        print("Message Received forme".format(wAddressString))
        if wAddressString not in self.mParticipantList.keys():
            wNewParticipant = Participant_Proxy(iAddress)
            self.mParticipantList[wAddressString] = wNewParticipant
            log("Participant {} joined".format(wAddressString))
        
        wCurrentProxy = self.mParticipantList[wAddressString]
        wCurrentProxy.mElapseTime = 0.0
        wCurrentProxy.processMessage(iMessage)

        for wKey, wProxy in self.mParticipantList.items():
            if wKey != wAddressString:
                if wProxy.checkSubscription(iMessage):
                    self.mUDPServer.send(iMessage, wProxy.mAddress)
    

class RTIFederate:
    def __init__(self, iCallback):
        self.mUDPClient = UDPClient(gRti_Server_Address, gRti_Server_Port, self.message)
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None
        self.mLastEntryPointTime = None
        self.mEventCallback = iCallback

    def startFederate(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mEntryPointThread = threading.Thread(target=self.entryPoint) 
        self.mEntryPointThread.start()

    def stopFederate(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        if None != self.mEntryPointThread:
            self.mRunning = False
            self.mEntryPointThread.join()
            self.mEntryPointThread = None
        self.mUDPClient.stopSocket()

    def entryPoint(self):
        self.mRunning = True

        while(self.mRunning):
            self.sendEvent("Ping".encode("utf8"))
            time.sleep((gRti_Participant_TimeOut+1)/2)

        print("Entry point Exited")

    def sendEvent(self, iEvent):
        self.mUDPClient.send(iEvent)

    def message(self, iMessage):
        if None != self.mEventCallback:
            self.mEventCallback(iMessage)
