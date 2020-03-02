import Common.rti as rti

def EventCallBack (iEvent):
    print(iEvent.decode("utf8"))

def main():
    wProcess = rti.RTIFederate(EventCallBack)
    wProcess.startFederate()

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
                else:
                    wProcess.sendData(wCmd[0], wCmd[1].encode("utf8"))
    
    print("While Loop Exited")
    wProcess.stopFederate()
    print("Prcess Stopped")


if "__main__":
    main()