import time, threading, json
import base64
import uuid 

from appCode.Common.utility import log
from .RTIFederate import RTIFederate, getRtiFederate
from .RTISetup import getRtiHash

class RTIObject:
    def __int__(self):
        self.mObject = None
        self.mElapseTime = 0.0
    
    def default(self, o):
        return o.__dict__    

    def __repr__(self):
        return 'Time : {} Object : {}'.format(self.mElapseTime, self.mObject)

class RTIObjectManager():
    def __init__(self, iRtiType, iRTIFederate, iTimeOut):
        self.mFederateRef = iRTIFederate
        self.mRtiType = "Object - {}".format(iRtiType)
        self.mOwnedObjects = {}
        self.mRemoteObjects = {}
        self.mStarted = False
        self.mLastIterationTime = time.time()
        self.mObjectTimeOut = iTimeOut
        self.mManagerId = uuid.uuid1()
        if self.mObjectTimeOut < 1.0:
            self.mObjectTimeOut = 1.0
        self.mLocalObjectEnterCallback = []
        self.mLocalObjectLeaveCallback = []
        self.mRemoteObjectEnterCallback = []
        self.mRemoteObjectLeaveCallback = []

    def startManager(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mFederateRef.subscribeToEventCallback(self.processEventCallback)
        self.mFederateRef.subscribeToType(self.mRtiType)
        self.mLastIterationTime = time.time()

    def stopManager(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        self.mFederateRef.unsubscribeFromEventCallback(self.processEventCallback)
        self.mFederateRef.unsubscribeFromType(self.mRtiType)
        self.mOwnedObjects.clear()
        self.mRemoteObjects.clear()

    def iteration(self):
        wCurrentTime = time.time()
        wDeltaTime = wCurrentTime - self.mLastIterationTime
        self.mLastIterationTime = wCurrentTime

        wSendTime = 2*self.mObjectTimeOut/3

        for wId, wObject in self.mOwnedObjects.items():
            if wObject.mElapseTime > wSendTime:
                self.sendObject(wId)
            else:
                wObject.mElapseTime += wDeltaTime
                  
        wDeleteList = []
        for wId, wFederateList in self.mRemoteObjects.items():
            for wFedId, wObject in wFederateList.items():
                if wObject.mElapseTime > self.mObjectTimeOut:
                        wDeleteList.append([wId, wFedId])
                else:            
                    wObject.mElapseTime += wDeltaTime
            
        for wKey in wDeleteList:
            wRObjectList = self.mRemoteObjects[wKey[0]]
                
            wJSONObject = json.loads(wRObjectList[wKey[1]].mObject)
            for wCallback in self.mRemoteObjectLeaveCallback:
                if None != wCallback:
                    wCallback( self.mRtiType, 0, wKey[1], wKey[0], wJSONObject)

            del wRObjectList[wKey[1]]
            if 0 == len(wRObjectList.items()):
                del self.mRemoteObjects[wKey[0]]

    def processEventCallback(self, iSource, iFederateId, iType, iData):
        if iType == self.mRtiType:
            wDecoded = iData.decode("utf8")
            wMessage = json.loads(wDecoded)
            if "id" not in wMessage:
                return

            if "object" not in wMessage:
                return
            wId = "{}".format(wMessage["id"])

            wObject = base64.b64decode(wMessage["object"].encode("utf8"))
            if self.mFederateRef.checkFederateId(iFederateId):
                print ("Object is owned")
                pass
            else:
                wObjectCreated = False
                wRemoteObject = None
                if wId not in self.mRemoteObjects:                
                    wRemoteObject = RTIObject()
                    wObjectCreated = True
                    self.mRemoteObjects[wId] = {}
                    self.mRemoteObjects[wId][iFederateId] = wRemoteObject
                else:
                    wRemoteObjectList = self.mRemoteObjects[wId] 
                    if iFederateId not in wRemoteObjectList:
                        wRemoteObject = RTIObject()
                        wObjectCreated = True
                        wRemoteObjectList[iFederateId] = wRemoteObject
                    else:
                        wRemoteObject = wRemoteObjectList[iFederateId]
                    
                wRemoteObject.mObject = wObject
                wRemoteObject.mElapseTime = 0

                if True == wObjectCreated:
                    wJSONObject = json.loads(wObject)
                    for wCallback in self.mRemoteObjectEnterCallback:
                        if None != wCallback:
                            wCallback( self.mRtiType, iSource, iFederateId, wId, wJSONObject)


    def sendObject(self, iObjectId):
        wObject = self.mOwnedObjects[iObjectId]
        wObject.time = 0
        wMessage = {}
        wMessage["id"] = iObjectId
        wMessage["object"] = base64.b64encode(wObject.mObject.encode("utf8")).decode("utf8")
        self.mFederateRef.sendData(self.mRtiType, json.dumps(wMessage).encode("utf8"))

    def setObject(self, iObjectId, iObject):
        wData = json.dumps(iObject)
        wSetObject = None
        if iObjectId not in self.mOwnedObjects:                
            wSetObject = RTIObject()
            self.mOwnedObjects[iObjectId] = wSetObject
        else:
            wSetObject = self.mOwnedObjects[iObjectId] 
            
        wSetObject.mObject = wData
        wSetObject.mElapseTime = self.mObjectTimeOut
        self.sendObject(iObjectId)

        wJSONObject = json.loads(wData)
        for wCallback in self.mLocalObjectEnterCallback:
            if None != wCallback:
                wCallback( self.mRtiType, 0, self.mFederateRef.mSelfId, iObjectId, wJSONObject)

    def getLocalObject(self, iObjectId):
        if iObjectId in self.mOwnedObjects:
            return json.loads(self.mOwnedObjects[iObjectId].mObject)
        return None

    def getRemoteObject(self, iObjectId):
        if iObjectId in self.mRemoteObjects:
            wContainer = {}
            for wKey, wItem in self.mRemoteObjects[iObjectId].items():
                wContainer[wKey]=json.loads(wItem.mObject)
            return wContainer
        return None

    def removeObject(self, iObjectId):
        if iObjectId in self.mOwnedObjects:
            wObject = self.mOwnedObjects[iObjectId]
            wJSONObject = json.loads(wObject.mObject)
            for wCallback in self.mLocalObjectLeaveCallback:
                if None != wCallback:
                    wCallback( self.mRtiType, 0, self.mFederateRef.mSelfId, iObjectId, wJSONObject)
            del self.mOwnedObjects[iObjectId]

    def subscribeRemoteObjectEnter(self, iCallback):
        if iCallback not in  self.mRemoteObjectEnterCallback:
            self.mRemoteObjectEnterCallback.append(iCallback)
    
    def unsubscribeRemoteObjectEnter(self, iCallback):
        self.mRemoteObjectEnterCallback = [wCallback for wCallback in self.mRemoteObjectEnterCallback if wCallback != iCallback]

    def subscribeRemoteObjectLeave(self,iCallback):
        if iCallback not in  self.mRemoteObjectLeaveCallback:
            self.mRemoteObjectLeaveCallback.append(iCallback)

    def unsubscribeRemoteObjectLeave(self, iCallback):
        self.mRemoteObjectLeaveCallback = [wCallback for wCallback in self.mRemoteObjectLeaveCallback if wCallback != iCallback]
        
    def subscribeLocalObjectEnter(self, iCallback):
        if iCallback not in  self.mLocalObjectEnterCallback:
            self.mLocalObjectEnterCallback.append(iCallback)

    def unsubscribeLocalObjectEnter(self, iCallback):
        self.mLocalObjectEnterCallback = [wCallback for wCallback in self.mLocalObjectEnterCallback if wCallback != iCallback]

    def subscribeLocalObjectLeave(self, iCallback):
        if iCallback not in  self.mLocalObjectLeaveCallback:
            self.mLocalObjectLeaveCallback.append(iCallback)

    def unsubscribeLocalObjectLeave(self, iCallback):
        self.mLocalObjectLeaveCallback = [wCallback for wCallback in self.mLocalObjectLeaveCallback if wCallback != iCallback]


gRTIObjectManagerDatabase = {}
def getRTIObjectManager(iObjectType):
    global gRTIObjectManagerDatabase
    wkey = getRtiHash(iObjectType)
    if wkey not in gRTIObjectManagerDatabase:
        wNewObjectManager = RTIObjectManager(iObjectType, getRtiFederate(), 1.0)
        gRTIObjectManagerDatabase[wkey] = wNewObjectManager
        wNewObjectManager.startManager()
        return wNewObjectManager
    else : 
        return gRTIObjectManagerDatabase[wkey] 

def stopAllRTIObjectManager():
    global gRTIObjectManagerDatabase
    for wKey, wManager in gRTIObjectManagerDatabase.items():
        wManager.stopManager()

        
def processAllRTIObjectManagerIteration():
    for wKey, wManager in gRTIObjectManagerDatabase.items():
        wManager.iteration()