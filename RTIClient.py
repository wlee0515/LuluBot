import Common.rti as rti
import json

def EventCallBack (iType, iEvent):
#    print("Callback 1 Type[{}] data[{}]".format(iType, iEvent.decode("utf8")))
    pass

def EventCallBack2 (iEvent):
 #   print("Callback 2 Type[{}] data[{}]".format(iType, iEvent.decode("utf8")))
    pass

def main():
    wProcess = rti.getRtiFederate()
    wManager = rti.RTIObjectManager("object",wProcess, 2)

    wProcess.startFederate()
    wManager.startManager()
    wProcess.subscribeToEventCallback(EventCallBack)
    wProcess.subscribeToEventCallback(EventCallBack2)

    while True:
        wInput = input("Enter Command : ")
        if wInput == "exit":
            break
        else:
            wCmd =  wInput.split(" ")
            if 2 <= len(wCmd):
                if "subscribe" == wCmd[0]:
                    wProcess.subscribeToType(wCmd[1])
                elif "unsubscribe" == wCmd[0]:
                    wProcess.unsubscribeFromType(wCmd[1])
                elif "object" == wCmd[0]:
                    wNewObject = {}
                    wNewObject["Data"] = wCmd[2]
                    wManager.setObject(wCmd[1],wNewObject)
                    
                elif "robject" == wCmd[0]:
                    wNewObject = {}
                    wManager.removeObject(wCmd[1])
                    
                elif "print" == wCmd[0]:
                    if "owned" == wCmd[1]:
                        print(wManager.mOwnedObjects)
                        
                    elif "remote" == wCmd[1]:
                        print(wManager.mRemoteObjects)
                        
                else:
                    wProcess.sendData(wCmd[0], wCmd[1].encode("utf8"))
    
    print("While Loop Exited")
    wManager.stopManager()
    wProcess.stopFederate()
    print("Prcess Stopped")


if "__main__":
    main()