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
        self.mRtiType = str(iRtiType)
        self.mOwnedObjects = {}
        self.mRemoteObjects = {}
        self.mStarted = False
        self.mRunning = False
        self.mObjectTimeOut = iTimeOut
        self.mManagerId = uuid.uuid1()
        if self.mObjectTimeOut < 1.0:
            self.mObjectTimeOut = 1.0

    def startManager(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mEntryPointThread = threading.Thread(target=self.entryPoint) 
        self.mEntryPointThread.start()
        self.mFederateRef.subscribeToEventCallback(self.processEventCallback)
        self.mFederateRef.subscribeToType(self.mRtiType)

    def stopManager(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        self.mFederateRef.unsubscribeFromEventCallback(self.processEventCallback)
        self.mFederateRef.unsubscribeFromType(self.mRtiType)
        if None != self.mEntryPointThread:
            self.mRunning = False
            self.mEntryPointThread.join()
            self.mEntryPointThread = None
        self.mOwnedObjects.clear()
        self.mRemoteObjects.clear()

    def entryPoint(self):
        self.mRunning = True
        wTimeOut = self.mObjectTimeOut
        wSleepTime =(wTimeOut+1)/10
        wLastTime = time.time()
        wSendTime = wTimeOut - wSleepTime

        while(self.mRunning):
            wCurrentTime = time.time()
            wDeltaTime = wCurrentTime - wLastTime
            for wId, wObject in self.mOwnedObjects.items():
                if wObject.mElapseTime > wSendTime:
                    self.sendObject(wId)
                else:
                    wObject.mElapseTime += wDeltaTime
                  
            wDeleteList = []
            for wId, wFederateList in self.mRemoteObjects.items():
                for wFedId, wObject in wFederateList.items():
                    if wObject.mElapseTime > wTimeOut:
                        wDeleteList.append([wId, wFedId])
                    else:            
                        wObject.mElapseTime += wDeltaTime
            
            for wKey in wDeleteList:
                wRObjectList = self.mRemoteObjects[wKey[0]]
                del wRObjectList[wKey[1]]
                if 0 == len(wRObjectList.items()):
                    del self.mRemoteObjects[wKey[0]]

            wLastTime = wCurrentTime
            time.sleep(wSleepTime)

        log("RTI Object Manager Entry point Exited")

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
                wRemoteObject = None
                if wId not in self.mRemoteObjects:                
                    wRemoteObject = RTIObject()
                    self.mRemoteObjects[wId] = {}
                    self.mRemoteObjects[wId][iFederateId] = wRemoteObject
                else:
                    wRemoteObjectList = self.mRemoteObjects[wId] 
                    if iFederateId not in wRemoteObjectList:
                        wRemoteObject = RTIObject()
                        wRemoteObjectList[iFederateId] = wRemoteObject
                    else:
                        wRemoteObject = wRemoteObjectList[iFederateId]
                    
                wRemoteObject.mObject = wObject
                wRemoteObject.mElapseTime = 0

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
            del self.mOwnedObjects[iObjectId]

gRTIObjectManagerDatabase = {}
def getRTIObjectManager(iObjectType):
    global gRTIObjectManagerDatabase
    if iObjectType not in gRTIObjectManagerDatabase:
        wNewObjeManager = RTIObjectManager(iObjectType, getRtiFederate(), 1.0)
        gRTIObjectManagerDatabase[iObjectType] = wNewObjeManager
        wNewObjeManager.startManager()
        return wNewObjeManager
    else : 
        return gRTIObjectManagerDatabase[iObjectType] 

def stopAllRTIObjectManager():
    global gRTIObjectManagerDatabase
    for wKey, wManager in gRTIObjectManagerDatabase.items():
        wManager.stopManager()