from Common.utility import log, taggedInput
from Device.pololu import SSC03A
from Device.socket import UDPClient

import time

def UDPCallBack(iMessage) :
    log(iMessage)
    return "Yes?".encode("utf8")

def main():

    wUDPSocket = UDPClient("localhost", 9000, UDPCallBack)

    wDevice = SSC03A("/dev/ttyAMA0", 1)
    time.sleep(1.0)

    wSimple_Protocal = True
    for i in range (0, 9):
      wAngle = i*10
      log("Setting angle to {}".format(wAngle))
      if True == wSimple_Protocal:
          for j in range(0,8):
             wDevice.setPosition_simpleProtocol(j, wAngle)
      else:
          for j in range(0,8):
             wDevice.setPosition(j,wAngle)
             wDevice.setSpeed(j,2)
      time.sleep(1)
    
    wInput = ""
    while("exit" != wInput) :
        wInput = taggedInput("Enter Command : ")
        wUDPSocket.send(wInput.encode("utf8"))
    wUDPSocket.stopSocket()

    

def test():
    Device = SSC03A()
    Device.setParameter(0,False, False, 10)
    Device.setSpeed(0,10)
    Device.set7BitPosition(0,0.5)
    Device.set8BitPosition(0,0.75)
    Device.setPosition(0,10)
    Device.setNeutralPosition(0,90)
    Device.checkServoNumberSetId()


if "__main__":
    main()