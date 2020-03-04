import time, threading, json
from appCode.Device.socket import UDPClient
from appCode.Common.utility import log
from .RTISetup import getRtiParticipantTimeOut, getRtiServerHash, getRtiServerAddress, getRtiServerPort, getRtiDebugMode
import base64
import uuid 

gRTIFederate = None
def getRtiFederate():
    global gRTIFederate
    if None == gRTIFederate:
        gRTIFederate = RTIFederate()
    return gRTIFederate



class RTIFederate:
    def __init__(self):
        self.mUDPClient = UDPClient(getRtiServerAddress(), getRtiServerPort(), self.message)
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None
        self.mLastEntryPointTime = None
        self.mEventCallbackList = []
        self.mLastMessageTime = 0
        self.mSubscriptionList = []
        self.mUpdateSubsciption = False
        self.mSelfId = hash(uuid.uuid1())

    def subscribeToEventCallback(self, iCallback):
        if iCallback not in self.mEventCallbackList:
            self.mEventCallbackList.append(iCallback)
    
    def unsubscribeFromEventCallback(self, iCallback):
        self.mEventCallbackList = [wCallback for wCallback in self.mEventCallbackList if wCallback != iCallback]
        
    def startFederate(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mEntryPointThread = threading.Thread(target=self.entryPoint) 
        self.mEntryPointThread.start()
        log("Rti Federate Started")

    def stopFederate(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        if None != self.mEntryPointThread:
            self.mRunning = False
            self.mEntryPointThread.join()
            self.mEntryPointThread = None
        self.mUDPClient.stopSocket()
        log("Rti Federate Stopped")

    def entryPoint(self):
        self.mRunning = True
        wTimeOut = getRtiParticipantTimeOut()
        wPingTime = (wTimeOut+1)/2
        wCheckTime = wPingTime/10
        while(self.mRunning):
            if True == self.mUpdateSubsciption:
                self.sendUpdateSubsciptionEvent()
                self.mUpdateSubsciption = False
            
            else:
                wTimeSinceLastMessage = time.time() - self.mLastMessageTime
                if wTimeSinceLastMessage > wPingTime:
                    self.sendMessage("ping".encode("utf8"))
            time.sleep(wCheckTime)

        log("RTI Federate Entry point Exited")

    def sendMessage(self, iEvent):
        
        if getRtiDebugMode():
            log("Sending : {}".format(iEvent))
        self.mUDPClient.send(iEvent)
        self.mLastMessageTime = time.time()

    def message(self, iMessage):
        try:
            wEvent = json.loads(iMessage.decode("utf8"))
            self.processEvent(wEvent)
        except:
            pass

    def subscribeToType(self, iType):
        if type(iType) == str:
            if iType not in self.mSubscriptionList:
                self.mSubscriptionList.append(iType)
                self.mUpdateSubsciption = True
                return True
        return False
    
    def unsubscribeFromType(self, iType):
        if type(iType) == str:
            if iType in self.mSubscriptionList:
                self.mSubscriptionList = [wType for wType in self.mSubscriptionList if wType != iType]
                self.mUpdateSubsciption = True
                return True
        return False

    def sendUpdateSubsciptionEvent( self):
        wEvent = {}
        wEvent["task"] = "subscribe"
        wEvent["list"] = self.mSubscriptionList
        wEventString = json.dumps(wEvent)
        self.sendMessage(wEventString.encode("utf8"))

    def sendData( self, iType, iData):
        wEvent = {}
        wEvent["task"] = "transfer"
        wEvent["type"] = iType
        wEvent["id"] = self.mSelfId
        wEvent["data"] = base64.b64encode(iData).decode("utf8")
        wEventString = json.dumps(wEvent)
        self.sendMessage(wEventString.encode("utf8"))

    def processEvent(self, iEvent):
        if getRtiDebugMode():
            log("processing Event : {}".format(json.dumps(iEvent)))

        if "source" not in iEvent:
            return

        wSource = iEvent["source"]
        if type(wSource) != int:
            return
            
        if "task" in iEvent:
                    
            wTask = iEvent["task"]
            if "subscribe" == wTask:
                print("{}  == {}".format(wSource, getRtiServerHash()))
                if wSource == getRtiServerHash():
                    self.sendUpdateSubsciptionEvent()
            
            elif "transfer" == wTask:

                if "type" not in iEvent:
                    return

                if "data" not in iEvent:
                    return

                if "id" not in iEvent:
                    return

                print("transfer checked")
                wId = iEvent["id"]
                if type(wId) != int:
                    return

                wType = iEvent["type"]
                if type(wType) != str:
                    return
                    
                wData = base64.b64decode(iEvent["data"].encode("utf8"))

                for wCallback in self.mEventCallbackList:
                    if None != wCallback:
                        wCallback(wId , wType, wData)
    
    def checkSelfId(self, iId):
        return self.mSelfId == iId