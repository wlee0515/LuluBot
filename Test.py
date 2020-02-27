from Device.pololu import SSC03A

import time

def main():
    wDevice = SSC03A("/dev/ttyAMA0", 1)
    time.sleep(1.0)

    wSimple_Protocal = True
    for i in range (0, 9):
      wAngle = i*10
      print("Setting angle to {}".format(wAngle))
      if True == wSimple_Protocal:
          for j in range(0,8):
             wDevice.setPosition_simpleProtocol(j, wAngle)
      else:
          for j in range(0,8):
             wDevice.setPosition(j,wAngle)
             wDevice.setSpeed(j,2)
#             time.sleep(0.01)
      time.sleep(1)

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