from appCode.Common.utility import log, taggedInput
import appCode.Common.ServiceManager as ServiceManager
import appCode.Common.rti as rti

import time, threading
import pprint

pp = pprint.PrettyPrinter(indent=4)


class InputConsole(ServiceManager.Service):

    def __init__(self):
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None
        
    def startService(self):
        if True == self.mStarted:
            return
        log("Inoput Console Start")
        self.mStarted = True
        self.mEntryPointThread = threading.Thread(target=self.entryPoint) 
        self.mEntryPointThread.setDaemon(True)
        self.mEntryPointThread.start()
        log("Inoput Console Start End")
      
    def entryPoint(self):
        self.mRunning = True
        while self.mRunning:
            wInput = taggedInput("Enter Command : ")
            wCmd =  wInput.split(" ")

            if "end_event" == wCmd[0]:
                wNewObject = {}
                wNewObject["EndProcess"] = True
                wNewObject["target"] = "All"     
                if 2 <= len(wCmd):
                    wNewObject["target"] = int (wCmd[1])    
                rti.getRTIEventManager("process_change").sendEvent(wNewObject)

            elif "print" == wCmd[0]:
                if 2 <= len(wCmd):
                    if "local" == wCmd[1]:                    
                        if 3 <= len(wCmd):
                            wType = wCmd[2]
                            if 4 <= len(wCmd):
                                wObject = rti.getRTIObjectManager(wType).getLocalObject(wCmd[3])
                                pp.pprint(wObject)
                            else:
                                pp.pprint(rti.getRTIObjectManager(wType).mOwnedObjects)

                    elif "remote" == wCmd[1]:
                        if 3 <= len(wCmd):
                            wType = wCmd[2]
                            if 4 <= len(wCmd):
                                wObject = rti.getRTIObjectManager(wType).getRemoteObject(wCmd[3])
                                pp.pprint(wObject)
                            else:
                                pp.pprint(rti.getRTIObjectManager(wType).mRemoteObjects)

            elif "event" == wCmd[0]:
                if 3 <= len(wCmd):
                    wNewObject = {}
                    wNewObject["BangBang"] = wCmd[2]
                    rti.getRTIEventManager(wCmd[1]).sendEvent(wNewObject)

            elif "object" == wCmd[0]:
                if 3 <= len(wCmd):
                    wNewObject = {}
                    wNewObject["Data"] = wCmd[2]
                    rti.getRTIObjectManager("object").setObject(wCmd[1],wNewObject)

            elif "subscribe" == wCmd[0]:
                if 2 <= len(wCmd):
                    rti.getRtiFederate().subscribeToType(wCmd[1])

            elif "unsubscribe" == wCmd[0]:
                if 2 <= len(wCmd):
                    rti.getRtiFederate().subscribeToType(wCmd[1])
            time.sleep(1.0)


    def stopService(self):
        if False == self.mStarted:
            return
        log("Inoput Console End")
        self.mStarted = False
        if None != self.mEntryPointThread:
            self.mRunning = False
            self.mEntryPointThread.join()
            self.mEntryPointThread = None
        pass
       

ServiceManager.initService("LuluBotUserInputConsole", True, InputConsole)

