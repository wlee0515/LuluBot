import time, threading
import json
from Device.socket import UDPServer
from Common.utility import log
from .RTISetup import getRtiParticipantTimeOut, getRtiServerPort

class Participant_Proxy:
    def __init__(self, iAddress):
        self.mAddress = iAddress
        self.mElapseTime = 0
        self.mSubscriptionList = {}

    def setSubscriptionList(self, iList):
        self.mSubscriptionList = [] 
        for item in iList:
            if type(item) == str:
                self.mSubscriptionList.append(item)

    def processMessage(self, iMessage):
        log(iMessage)
        return True

    def checkSubscription(self, iSubscribedType):
        return iSubscribedType in self.mSubscriptionList

class RTIProcess:
    def __init__(self):
        self.mUDPServer = UDPServer(getRtiServerPort(), self.message)
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
        wTimeOut = getRtiParticipantTimeOut()
        wSleepTime =(wTimeOut+1)/10
        log("Entry point started with participant Timeout at {} s".format(wTimeOut))
        wLastTime = time.time()


        while(self.mRunning):
            wCurrentTime = time.time()
            wDeltaTime = wCurrentTime - wLastTime
            wDeleteList = []
            for wKey, wProxy in self.mParticipantList.items():
                if wProxy.mElapseTime > wTimeOut:
                    wDeleteList.append(wKey)
                else:            
                    wProxy.mElapseTime += wDeltaTime
                  
            
            for wItem in wDeleteList:
                wProxy = self.mParticipantList[wKey]
                wAddressString = "{}:{}".format(*wProxy.mAddress)
                log("Participant {} left".format(wAddressString))
                del self.mParticipantList[wKey]

            wLastTime = wCurrentTime
            time.sleep(wSleepTime)

        log("Entry point Exited")


    def message(self, iMessage, iAddress):
        wAddressString = "{}:{}".format(*iAddress)
        if wAddressString not in self.mParticipantList.keys():
            wNewParticipant = Participant_Proxy(iAddress)
            self.mParticipantList[wAddressString] = wNewParticipant
            log("Participant {} joined".format(wAddressString))
            self.sendUpdateSubsciptionEvent(iAddress)

        self.mParticipantList[wAddressString].mElapseTime = 0
        
        try:
            wEvent = json.loads(iMessage.decode("utf8"))
            self.processEvent(wEvent, wAddressString)
        except:
            pass

    def sendUpdateSubsciptionEvent(self, iAddress):
        wEvent = {}
        wEvent["task"] = "subscribe"
        wEventString = json.dumps(wEvent)
        self.mUDPServer.send(wEventString.encode("utf8"), iAddress)

    def processEvent(self, iEvent, iParticipant):
        log("{} : {}".format(iParticipant, json.dumps(iEvent)))
        wTask = iEvent["task"]
        if "task" in iEvent:
            wTask = iEvent["task"]
            if "subscribe" == wTask:
                if "list" in iEvent:
                    wCurrentProxy = self.mParticipantList[iParticipant]
                    wCurrentProxy.setSubscriptionList(iEvent["list"])
                    log("{}".format(wCurrentProxy.mSubscriptionList))
            
            elif "transfer" == wTask:
                if "type" not in iEvent:
                    return
                if "data" not in iEvent:
                    return
                    
                wType = iEvent["type"]
                if type(wType) != str:
                    return
                    
                wEventString = json.dumps(iEvent)
                
                for wKey, wProxy in self.mParticipantList.items():
                    if wKey != iParticipant:
                        if wProxy.checkSubscription(wType):
                            self.mUDPServer.send(wEventString.encode("utf8"), wProxy.mAddress)