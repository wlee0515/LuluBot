import time
import json
from appCode.Device.socket import UDPServer
from appCode.Common.utility import log
from .RTISetup import getRtiParticipantTimeOut, getRtiServerHash, getRtiHash, getRtiHashAddress, getRtiServerPort, getRtiDebugMode

class Participant_Proxy:
    def __init__(self, iAddress):
        self.mAddress = iAddress
        self.mElapseTime = 0
        self.mSubscriptionList = {}
        self.mSubscriptionListHash = {}

    def setSubscriptionList(self, iList):
        self.mSubscriptionList = [] 
        self.mSubscriptionListHash = []
        for item in iList:
            if type(item) == str:
                self.mSubscriptionList.append(item)
                self.mSubscriptionListHash.append(getRtiHash(item))

    def processMessage(self, iMessage):
        log(iMessage)
        return True

    def checkSubscription(self, iSubscribedType):
        return iSubscribedType in self.mSubscriptionList

    def checkSubscriptionHash(self, iSubscribedTypeHash):
        return iSubscribedTypeHash in self.mSubscriptionListHash

class RTIServer:
    def __init__(self):
        self.mUDPServer = UDPServer(getRtiServerPort(), self.message)
        self.mParticipantList = {}
        self.mStarted = False
        self.mLastIterationTime = time.time()
        self.mServerHash = getRtiServerHash()

    def startServer(self):
        if True == self.mStarted:
            return
        self.mStarted = True
        self.mLastIterationTime = time.time()
        self.mUDPServer.startServer()
        wTimeOut = getRtiParticipantTimeOut()
        log("Entry point started with participant Timeout at {} s".format(wTimeOut))

    def stopServer(self):
        if False == self.mStarted:
            return
        self.mStarted = False
        self.mUDPServer.stopServer()
        self.mParticipantList.clear()

    def iteration(self):
        wNewTime = time.time()
        wDeltaTime = wNewTime - self.mLastIterationTime
        self.mLastIterationTime = wNewTime
        
        wTimeOut = getRtiParticipantTimeOut()

        wDeleteList = []
        for wKey, wProxy in self.mParticipantList.items():
            if wProxy.mElapseTime > wTimeOut:
                wDeleteList.append(wKey)
            else:            
                wProxy.mElapseTime += wDeltaTime
                  
        for wKey in wDeleteList:
            wProxy = self.mParticipantList[wKey]
            wAddressString = "{}:{}".format(*wProxy.mAddress)
            log("Participant {} left".format(wAddressString))
            del self.mParticipantList[wKey]

    def message(self, iMessage, iAddress):
        wAddressString = "{}:{}".format(*iAddress)
        wKey = getRtiHashAddress(*iAddress)
        if wKey not in self.mParticipantList.keys():
            wNewParticipant = Participant_Proxy(iAddress)
            self.mParticipantList[wKey] = wNewParticipant
            log("Participant {} joined".format(wAddressString))
            self.sendUpdateSubsciptionEvent(iAddress)

        self.mParticipantList[wKey].mElapseTime = 0
        
        try:
            wEvent = json.loads(iMessage.decode("utf8"))
            self.processEvent(wEvent, wKey)
        except:
            pass

    def sendUpdateSubsciptionEvent(self, iAddress):
        wEvent = {}
        wEvent["task"] = "subscribe"
        wEvent["source"] = self.mServerHash
        wEventString = json.dumps(wEvent)
        self.mUDPServer.send(wEventString.encode("utf8"), iAddress)

    def processEvent(self, iEvent, iParticipant):
        if getRtiDebugMode():
            log("process Event : {} : {}".format(iParticipant, json.dumps(iEvent)))
        wTask = iEvent["task"]
        if "task" in iEvent:
            wTask = iEvent["task"]
            if "subscribe" == wTask:
                if "list" in iEvent:
                    wCurrentProxy = self.mParticipantList[iParticipant]
                    wCurrentProxy.setSubscriptionList(iEvent["list"])
                    log("Participant [{}] subscriptions {}".format(iParticipant, wCurrentProxy.mSubscriptionList))
            
            elif "transfer" == wTask:
                if "type" not in iEvent:
                    return
                if "data" not in iEvent:
                    return
                    
                wType = iEvent["type"]
                if type(wType) != str:
                    return
                    
                iEvent["source"] = iParticipant
                wEventString = json.dumps(iEvent)
                
                wTypeHash = getRtiHash(wType)
                for wKey, wProxy in self.mParticipantList.items():
                    if wKey != iParticipant:
                        if wProxy.checkSubscriptionHash(wTypeHash):
                            self.mUDPServer.send(wEventString.encode("utf8"), wProxy.mAddress)

