import time, json
import base64
import uuid 

from appCode.Common.utility import log
from .RTIFederate import RTIFederate, getRtiFederate
from .RTISetup import getRtiHash

class RTIEventManager():
    def __init__(self, iRtiType, iRTIFederate):
        self.mFederateRef = iRTIFederate
        self.mRtiType = "Event - {}".format(iRtiType)
        self.mStarted = False
        self.mEventCallback = []

    def startManager(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mFederateRef.subscribeToEventCallback(self.processEventCallback)
        self.mFederateRef.subscribeToType(self.mRtiType)

    def stopManager(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        self.mFederateRef.unsubscribeFromEventCallback(self.processEventCallback)
        self.mFederateRef.unsubscribeFromType(self.mRtiType)

    def processEventCallback(self, iSource, iFederateId, iType, iData):
        if iType == self.mRtiType:
            wDecoded = iData.decode("utf8")
            wMessage = json.loads(wDecoded)

            if "event" not in wMessage:
                return
                
            wEvent = base64.b64decode(wMessage["event"].encode("utf8"))
            wJSONObject = json.loads(wEvent)

            for wCallback in self.mEventCallback:
                if None != wCallback:
                    wCallback( self.mRtiType, iSource, iFederateId, wJSONObject)

    def sendEventRemote(self, iEvent):
        wMessage = {}
        wMessage["event"] = base64.b64encode(json.dumps(iEvent).encode("utf8")).decode("utf8")
        self.mFederateRef.sendData(self.mRtiType, json.dumps(wMessage).encode("utf8"))

    def sendEventLocal(self, iEvent):
        for wCallback in self.mEventCallback:
            if None != wCallback:
                wCallback( self.mRtiType, 0, self.mFederateRef.mSelfId, iEvent)

    def sendEvent(self, iEvent):
        self.sendEventLocal( iEvent)
        self.sendEventRemote( iEvent)

    def subscribeEventCallback(self, iCallback):
        if iCallback not in  self.mEventCallback:
            self.mEventCallback.append(iCallback)
    
    def unsubscribeEventCallback(self, iCallback):
        self.mEventCallback = [wCallback for wCallback in self.mEventCallback if wCallback != iCallback]


gRTIEventManagerDatabase = {}
def getRTIEventManager(iObjectType):
    global gRTIEventManagerDatabase
    wkey = getRtiHash(iObjectType)
    if wkey not in gRTIEventManagerDatabase:
        wNewEventManager = RTIEventManager(iObjectType, getRtiFederate())
        gRTIEventManagerDatabase[wkey] = wNewEventManager
        wNewEventManager.startManager()
        return wNewEventManager
    else : 
        return gRTIEventManagerDatabase[wkey] 

def stopAllRTIEventManager():
    global gRTIEventManagerDatabase
    for wKey, wManager in gRTIEventManagerDatabase.items():
        wManager.stopManager()