import appCode.Common.rti as rti
import appCode.Service
import appCode.Common.ServiceManager as ServiceManager

import json
import sys
import pprint

pp = pprint.PrettyPrinter(indent=4)

def startFuntion(iContext):
    iContext["Service"].startService()

def stopFunction(iContext):
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
                    rti.getRTIObjectManager("object").setObject(wCmd[1],wNewObject)

            elif "robject" == wCmd[0]:
                wNewObject = {}
                rti.getRTIObjectManager("object").removeObject(wCmd[1])

            elif "print" == wCmd[0]:
                if "local" == wCmd[1]:
                    if 3 <= len(wCmd):
                        wObject = rti.getRTIObjectManager("object").getLocalObject(wCmd[2])
                        pp.pprint(wObject)
                    else:
                        pp.pprint(rti.getRTIObjectManager("object").mOwnedObjects)

                elif "remote" == wCmd[1]:
                    if 3 <= len(wCmd):
                        wObject = rti.getRTIObjectManager("object").getRemoteObject(wCmd[2])
                        pp.pprint(wObject)
                    else:
                        pp.pprint(rti.getRTIObjectManager("object").mRemoteObjects)
                    



def main():
    
    iContext = {}
    iContext["Service"] = ServiceManager.getServiceManager()


    iContext["ProcessControl"] = rti.RTIProcessControl( startFuntion, iterationFunction, stopFunction)
    iContext["ProcessControl"].run(10, iContext)
    
    print("Prcess Stopped")



if "__main__":
    main()