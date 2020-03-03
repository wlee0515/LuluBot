import os

gServiceManager = None
def getServiceManager():
    global gServiceManager
    if None == gServiceManager:
        gServiceManager = ServiceManager()
    return gServiceManager

def initService_always(iService):
    getServiceManager().addService(iService())
    print("Service [{}] added".format(iService))

def initService(iEnv, iValue, iService):
    if iEnv in os.environ:
        if os.environ[iEnv] == str(iValue):
            getServiceManager().addService(iService())
            print("Service [{}] added".format(iService))
            return True
    return False

class Service():
    def __init__(self):
        pass
    
    def startService(self):
        pass
      
    def stopService(self):
        pass
       

class ServiceManager(Service):

    def __init__(self):
        self.mServiceList = []

    def addService(self, iService):
        self.mServiceList.append(iService)

    def startService(self):
        for wService in self.mServiceList:
            wService.startService()
            
    def stopService(self):
        for wService in self.mServiceList:
            wService.stopService()
            
           