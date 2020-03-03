import appCode.Common.ServiceManager as ServiceManager

class Service2(ServiceManager.Service):

    
    def startService(self):
        print("service 2 start")
        pass
      
    def stopService(self):
        print("service 2 stop")
        pass
       

ServiceManager.initService("Service", 1, Service2)
