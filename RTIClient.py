import appCode.Common.rti as rti
import json
import appCode.Service
import appCode.Common.ServiceManager as ServiceManager

def EventCallBack (iType, iEvent):
#    print("Callback 1 Type[{}] data[{}]".format(iType, iEvent.decode("utf8")))
    pass

def main():
    wFederate = rti.getRtiFederate()
    wObjManager = rti.RTIObjectManager("object",wFederate, 2)
    wServiceManager = ServiceManager.getServiceManager()

    wFederate.startFederate()
    wObjManager.startManager()
    wServiceManager.startService()
    wFederate.subscribeToEventCallback(EventCallBack)

    while True:
        wInput = input("Enter Command : ")
        if wInput == "exit":
            break
        else:
            wCmd =  wInput.split(" ")
            if 2 <= len(wCmd):
                if "subscribe" == wCmd[0]:
                    wFederate.subscribeToType(wCmd[1])
                elif "unsubscribe" == wCmd[0]:
                    wFederate.unsubscribeFromType(wCmd[1])
                elif "object" == wCmd[0]:
                    wNewObject = {}
                    wNewObject["Data"] = wCmd[2]
                    wObjManager.setObject(wCmd[1],wNewObject)
                    
                elif "robject" == wCmd[0]:
                    wNewObject = {}
                    wObjManager.removeObject(wCmd[1])
                    
                elif "print" == wCmd[0]:
                    if "owned" == wCmd[1]:
                        print(wObjManager.mOwnedObjects)
                        
                    elif "remote" == wCmd[1]:
                        print(wObjManager.mRemoteObjects)
                        
                else:
                    wFederate.sendData(wCmd[0], wCmd[1].encode("utf8"))
    
    print("While Loop Exited")
    
    wServiceManager.stopService()
    wObjManager.stopManager()
    wFederate.stopFederate()
    print("Prcess Stopped")


if "__main__":
    main()