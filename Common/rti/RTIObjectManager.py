import time, threading, json
from .RTIFederate import RTIFederate
import base64

class RTIObject:
    def __int__(self):
        self.mObject = None
        self.mElapseTime = 0.0
    
    def default(self, o):
        return o.__dict__    

class RTIObjectManager():
    def __init__(self, iRtiType, iRTIFederate, iTimeOut):
        self.mFederateRef = iRTIFederate
        self.mRtiType = iRtiType
        self.mOwnedObjects = {}
        self.mRemoteObjects = {}
        self.mStarted = False
        self.mRunning = False
        self.mObjectTimeOut = iTimeOut
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
        wSendTime =wTimeOut - wSleepTime

        while(self.mRunning):
            wCurrentTime = time.time()
            wDeltaTime = wCurrentTime - wLastTime
            for wId, wObject in self.mOwnedObjects.items():
                if wObject.mElapseTime > wSendTime:
                    self.sendObject(wId)
                else:            
                    wObject.mElapseTime += wDeltaTime
                  
            wDeleteList = []
            for wId, wObject in self.mRemoteObjects.items():
                if wObject.mElapseTime > wTimeOut:
                    wDeleteList.append(wId)
                else:            
                    wObject.mElapseTime += wDeltaTime
            
            for wKey in wDeleteList:
                del self.mRemoteObjects[wKey]

            wLastTime = wCurrentTime
            time.sleep(wSleepTime)

        log("Entry point Exited")



    def processEventCallback(self, iType, iData):
        if iType == self.mRtiType:
            wDecoded = iData.decode("utf8")
            wMessage = json.loads(wDecoded)
            if "id" not in wMessage:
                return
            if "object" not in wMessage:
                return
            wId =  wMessage["id"]

            wObject = base64.b64decode(wMessage["object"].encode("utf8"))
            if wId in self.mOwnedObjects:
                pass
            else:
                wRemoteObject = None
                if wId not in self.mRemoteObjects:                
                    wRemoteObject = RTIObject()
                    self.mRemoteObjects[wId] = wRemoteObject
                else:
                    wRemoteObject = self.mRemoteObjects[wId] 
                    
                wRemoteObject.mObject = wObject
                wRemoteObject.mElapseTime = 0
            

    def sendObject(self, iObjectId):
        if iObjectId in self.mOwnedObjects:
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


    def getObject(self, iObjectId):
        if iObjectId in self.mOwnedObjects:
            return json.loads(self.mOwnedObjects[iObjectId])
        if iObjectId in self.mRemoteObjects:
            return json.loads(self.mRemoteObjects[iObjectId].object)
        return None
        
    def removeObject(self, iObjectId):
        if iObjectId in self.mOwnedObjects:
            del self.mOwnedObjects[iObjectId]