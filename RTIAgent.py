import appCode.Common.rti as rti
import appCode.Service
import appCode.Common.ServiceManager as ServiceManager

import json
import sys

def startFuntion(iContext):
    
    if "RTIServer" in iContext:
        iContext["RTIServer"].startServer()

    iContext["Federate"].startFederate()
    iContext["ObjectManager"].startManager()
    iContext["Service"].startService()

def stopFunction(iContext):    
    if "RTIServer" in iContext:
        iContext["RTIServer"].stopServer()
        
    iContext["Federate"].stopFederate()
    iContext["ObjectManager"].stopManager()
    iContext["Service"].stopService()


def iterationFunction(iContext):
    wInput = input("Enter Command : ")
    if wInput == "exit":
        iContext["ProcessControl"].endProcess()
    else:
        wCmd =  wInput.split(" ")
        if 2 <= len(wCmd):
            if "subscribe" == wCmd[0]:
                iContext["Federate"].subscribeToType(wCmd[1])

            elif "unsubscribe" == wCmd[0]:
                iContext["Federate"].unsubscribeFromType(wCmd[1])

            elif "object" == wCmd[0]:
                if 3 <= len(wCmd):
                    wNewObject = {}
                    wNewObject["Data"] = wCmd[2]
                    iContext["ObjectManager"].setObject(wCmd[1],wNewObject)

            elif "robject" == wCmd[0]:
                wNewObject = {}
                iContext["ObjectManager"].removeObject(wCmd[1])

            elif "print" == wCmd[0]:
                if "owned" == wCmd[1]:
                    print(iContext["ObjectManager"].mOwnedObjects)

                elif "remote" == wCmd[1]:
                    print(iContext["ObjectManager"].mRemoteObjects)



def main():
    
    iContext = {}
    if "-server" in sys.argv:
        iContext["RTIServer"] = rti.RTIServer()
        
    iContext["Federate"] = rti.getRtiFederate()
    iContext["ObjectManager"] = rti.RTIObjectManager("object", iContext["Federate"] , 2)
    iContext["Service"] = ServiceManager.getServiceManager()


    iContext["ProcessControl"] = rti.RTIProcessControl(iContext["Federate"], startFuntion, iterationFunction, stopFunction)
    iContext["ProcessControl"].run(10, iContext)
    
    print("Prcess Stopped")



if "__main__":
    main()