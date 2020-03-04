import os, sys, threading, time
from .RTIObjectManager import RTIObjectManager, getRTIObjectManager, stopAllRTIObjectManager
from .RTIFederate import getRtiFederate, stopRtiFederate
from .RTIServer import RTIServer
from appCode.Common.utility import getProcessName, getStartTime

class RTIProcessControl:
    def __init__(self, iProcessStartFunction, iProcessIterationFunction,  iProcessStopFunction):
        self.mProcessStatus = {}
        self.mProcessStatus["Name"] = getProcessName()
        self.mProcessStatus["StartTime"] = getStartTime()
        self.mProcessStatus["IsHost"] = False

        if "=host" in sys.argv:
            self.mProcessStatus["IsHost"] = True

        self.mProcessStartFunction = iProcessStartFunction
        self.mProcessIterationFunction = iProcessIterationFunction
        self.mProcessStopFunction = iProcessStopFunction
        self.mRunning = False
        self.mStarted = False
        self.mEnd = False
        self.mMonitorThread = None
        self.mIsHost = "-rtiProcCtrlHost" in sys.argv 
        

    def setProcessPhase(self, iPhase):
        wObjectManager = getRTIObjectManager("process_state")
        self.mProcessStatus["phase"] = "{}".format(iPhase)
        wObjectManager.setObject("status", self.mProcessStatus)
        
    def processStatusObjectEnter(self, iType, iSourceId, iFerderateId, iObjectId, iObject):
        print("Enter {}-{}-{}-{}-{}".format(iType, iSourceId, iFerderateId, iObjectId, iObject))

    def processStatusObjectLeave(self, iType, iSourceId, iFerderateId, iObjectId, iObject):
        print("Exit {}-{}-{}-{}-{}".format(iType, iSourceId, iFerderateId, iObjectId, iObject))

    def endProcess(self):
        self.mEnd = True

    def __selfIteration__(self, iContext):
        if None != self.mProcessIterationFunction:
            print("hello")
            self.mProcessIterationFunction(iContext)

    def __MonitorThread__(self, iTimeStep):
        self.mEnd = False
        wTimeStep = iTimeStep
        if wTimeStep < 0.001:
            wTimeStep = 0.001
        if wTimeStep > 1.0:
            wTimeStep = 1.0

        while False == self.mEnd:
          

            time.sleep(wTimeStep)

        self.mRunning = False

    def run(self, iFrequency, iContext):
        if True == self.mStarted:
            return

        wOneShotProcess = False
        wTimeStep = 1
        if iFrequency < 0.0:
            wOneShotProcess = True
        else:
            wTimeStep = 1/iFrequency

        self.setProcessPhase("starting")
        self.mMonitorThread = threading.Thread(target= self.__MonitorThread__, args=(wTimeStep,)) 
        self.mMonitorThread.start()

        wObjectManager = getRTIObjectManager("process_state")
        wObjectManager.subscribeLocalObjectEnter(self.processStatusObjectEnter)
        wObjectManager.subscribeRemoteObjectEnter(self.processStatusObjectEnter)
        wObjectManager.subscribeLocalObjectLeave(self.processStatusObjectLeave)
        wObjectManager.subscribeRemoteObjectLeave(self.processStatusObjectLeave)

        wRTIServer = None
        if "-server" in sys.argv:
            wRTIServer = RTIServer()
            wRTIServer.startServer()

        if None != self.mProcessStartFunction:
            self.mProcessStartFunction(iContext)

        self.setProcessPhase("running")

        if wOneShotProcess:
            self.__selfIteration__(iContext)
        else:
            self.mRunning = True
            while(self.mRunning):
                self.mProcessIterationFunction(iContext)
                time.sleep(wTimeStep)

        if None != self.mProcessStopFunction:
            self.mProcessStopFunction(iContext)

        self.setProcessPhase("stopping")

        wObjectManager.unsubscribeLocalObjectEnter(self.processStatusObjectEnter)
        wObjectManager.unsubscribeRemoteObjectEnter(self.processStatusObjectEnter)
        wObjectManager.unsubscribeLocalObjectLeave(self.processStatusObjectLeave)
        wObjectManager.unsubscribeRemoteObjectLeave(self.processStatusObjectLeave)

        stopAllRTIObjectManager()
        stopRtiFederate()

        if None != wRTIServer:
            wRTIServer.stopServer()

        self.endProcess()
        if None != self.mMonitorThread:
            self.mMonitorThread.join()
            self.mMonitorThread = None

        self.mStarted = False