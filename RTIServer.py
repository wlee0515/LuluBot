import Common.rti as rti

def main():
    wProcess = rti.RTIProcess()
    wProcess.startServer()

    while True:
        wInput = input("Enter Command : ")
        if wInput == "exit":
            break

    print("While Loop Exited")
    wProcess.stopServer()
    print("Prcess Stopped")



if "__main__":
    main()