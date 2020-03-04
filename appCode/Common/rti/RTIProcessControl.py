import os, sys, threading, time
from .RTIObjectManager import RTIObjectManager
from .RTIFederate import getRtiFederate

class RTIProcessStatus:
    def __init__(self):
        self.mProcessName = ""
        self.mProcessMode = "NA"

class RTIProcessControl:
    def __init__(self, iRTIFederate, iProcessStartFunction, iProcessIterationFunction,  iProcessStopFunction):
        self.mProcessStatus = RTIProcessStatus()
        self.mRTIProcessStatus = RTIObjectManager("process_status", iRTIFederate, 2)
        self.mProcessStartFunction = iProcessStartFunction
        self.mProcessIterationFunction = iProcessIterationFunction
        self.mProcessStopFunction = iProcessStopFunction
        self.mRunning = False
        self.mStarted = False
        self.mEnd = False
        self.mMonitorThread = None
        self.mIsHost = "-rtiProcCtrlHost" in sys.argv 

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

        self.mRTIProcessStatus.startManager()
        self.mMonitorThread = threading.Thread(target= self.__MonitorThread__, args=(wTimeStep,)) 
        self.mMonitorThread.start()

        if None != self.mProcessStartFunction:
            self.mProcessStartFunction(iContext)

        if wOneShotProcess:
            self.__selfIteration__(iContext)
        else:
            self.mRunning = True
            while(self.mRunning):
                self.mProcessIterationFunction(iContext)
                time.sleep(wTimeStep)

        if None != self.mProcessStopFunction:
            self.mProcessStopFunction(iContext)

        self.mRTIProcessStatus.stopManager()
        
        self.endProcess()
        if None != self.mMonitorThread:
            self.mMonitorThread.join()
            self.mMonitorThread = None

        self.mStarted = False