import appCode.Common.rti as rti
import appCode.Common.ServiceManager as ServiceManager
import appCode.Service

import json
import sys

def startFuntion(iContext):
    iContext["Service"].startService()

def stopFunction(iContext):
    iContext["Service"].stopService()


def iterationFunction(iContext):
    return


def main():
    
    iContext = {}
    iContext["Service"] = ServiceManager.getServiceManager()


    iContext["ProcessControl"] = rti.RTIProcessControl( startFuntion, iterationFunction, stopFunction)
    iContext["ProcessControl"].run(10, iContext)
    
    print("Prcess Stopped")



if "__main__":
    main()