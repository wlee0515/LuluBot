import os, sys, threading, time
from .RTIObjectManager import getRTIObjectManager, stopAllRTIObjectManager
from .RTIEventManager import getRTIEventManager, stopAllRTIEventManager
from .RTIFederate import getRtiFederate, stopRtiFederate
from .RTIServer import RTIServer
from appCode.Common.utility import getProcessName, getStartTime, log

class RTIProcessControl:
    def __init__(self, iProcessStartFunction, iProcessIterationFunction,  iProcessStopFunction):
        self.mProcessStatus = {}
        self.mProcessStatus["Name"] = getProcessName()
        self.mProcessStatus["StartTime"] = getStartTime()
        self.mProcessStatus["IsHost"] = False

        if "-rtiProcCtrlHost" in sys.argv:
            self.mProcessStatus["IsHost"] = True

        self.mProcessStartFunction = iProcessStartFunction
        self.mProcessIterationFunction = iProcessIterationFunction
        self.mProcessStopFunction = iProcessStopFunction
        self.mRunning = False
        self.mStarted = False
        self.mEnd = False
        self.mIterationThread = None
        self.mHostList = {}
        
    def isCurrentProcessHost(self):
        return self.mProcessStatus["IsHost"]

    def setProcessPhase(self, iPhase):
        log("Setting process phase to [{}]".format(iPhase))
        wObjectManager = getRTIObjectManager("process_state")
        self.mProcessStatus["phase"] = "{}".format(iPhase)
        wObjectManager.setObject("status", self.mProcessStatus)
        
    def processStatusObjectEnter(self, iType, iSourceId, iFederateId, iObjectId, iObject):
        if "IsHost" in iObject:
            if True == iObject["IsHost"]:
                if iSourceId not in self.mHostList:
                    self.mHostList[iSourceId] = {}
                self.mHostList[iSourceId][iFederateId] = True

    def processStatusObjectLeave(self, iType, iSourceId, iFederateId, iObjectId, iObject):
        if iSourceId in self.mHostList:
            if iFederateId in self.mHostList[iSourceId]:
                del self.mHostList[iSourceId][iFederateId]
            if 0 == len(self.mHostList[iSourceId]):
                del self.mHostList[iSourceId]

    def processProcessChangeEvent(self, iType, iSourceId, iFederateId, iEvent):
        log("Event {}-{}-{}-{}".format(iType, iSourceId, iFederateId, iEvent))
        if "EndProcess" in iEvent:
            if iSourceId not in self.mHostList:
                log("Source Id not registered as host")
                return
            if iFederateId not in self.mHostList[iSourceId]:
                log("Federate Id not registered as host")
                return    
            if True == iEvent["EndProcess"]:
                if "target" in iEvent:
                    if "All" == iEvent["target"] or (getRtiFederate().checkFederateId(iEvent["target"])):
                        log("End Event Accepted")
                        self.endProcess() 

    def endProcess(self):
        self.mEnd = True

    def __iterationThread__(self, iFrequency, iContext):
        if None == self.mProcessIterationFunction:
            return

        wOneShotProcess = False
        wTimeStep = 1
        if iFrequency < 0.0:
            wOneShotProcess = True
        else:
            wTimeStep = 1/iFrequency

        if wOneShotProcess:
            self.mProcessIterationFunction(iContext)
        else:
            self.mRunning = True
            while(self.mRunning):
                self.mProcessIterationFunction(iContext)
                time.sleep(wTimeStep)

    def run(self, iFrequency, iContext):
        if True == self.mStarted:
            return

        wObjectManager = getRTIObjectManager("process_state")
        wObjectManager.subscribeLocalObjectEnter(self.processStatusObjectEnter)
        wObjectManager.subscribeRemoteObjectEnter(self.processStatusObjectEnter)
        wObjectManager.subscribeLocalObjectLeave(self.processStatusObjectLeave)
        wObjectManager.subscribeRemoteObjectLeave(self.processStatusObjectLeave)

        wEventManager = getRTIEventManager("process_change")
        wEventManager.subscribeEventCallback(self.processProcessChangeEvent)
        
        wRTIServer = None
        if "-server" in sys.argv:
            wRTIServer = RTIServer()
            wRTIServer.startServer()

        self.setProcessPhase("starting")
        if None != self.mProcessStartFunction:
            self.mProcessStartFunction(iContext)

        self.setProcessPhase("running")
        self.mIterationThread = threading.Thread(target= self.__iterationThread__, args=(iFrequency,iContext)) 
        self.mIterationThread.setDaemon(True)
        self.mIterationThread.start()

        while False == self.mEnd:
            time.sleep(1.0)

        if None != self.mIterationThread:
            self.mRunning = False
            self.mIterationThread.join(5)
            self.mIterationThread = None

        if None != self.mProcessStopFunction:
            self.mProcessStopFunction(iContext)

        self.setProcessPhase("stopping")
        time.sleep(3.0)        
        self.setProcessPhase("stop")

        wObjectManager.unsubscribeLocalObjectEnter(self.processStatusObjectEnter)
        wObjectManager.unsubscribeRemoteObjectEnter(self.processStatusObjectEnter)
        wObjectManager.unsubscribeLocalObjectLeave(self.processStatusObjectLeave)
        wObjectManager.unsubscribeRemoteObjectLeave(self.processStatusObjectLeave)

        wEventManager.unsubscribeEventCallback(self.processProcessChangeEvent)
        
        stopAllRTIObjectManager()
        stopAllRTIEventManager()
        stopRtiFederate()

        if None != wRTIServer:
            wRTIServer.stopServer()

        self.mStarted = False