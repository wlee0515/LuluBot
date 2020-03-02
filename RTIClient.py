import Common.rti as rti

def EventCallBack (iEvent):
    print(iEvent)

def main():
    wProcess = rti.RTIFederate(EventCallBack)
    wProcess.startFederate()

    while True:
        wInput = input("Enter Command : ")
        if wInput == "exit":
            break
        else:
          wProcess.sendEvent(wInput)
    
    print("While Loop Exited")
    wProcess.stopFederate()
    print("Prcess Stopped")


if "__main__":
    main()