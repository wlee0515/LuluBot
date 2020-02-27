import serial
import sys
import time

class Device():
    def __init__(self, comport ="/dev/ttyACM0",timeout=1):
        self.comport = None
        self.isInitialized = False

        try:
            self.comport = serial.Serial(comport,timeout=timeout)
            self.comport.baudrate = 9600
            self.comport.baudrate =  2400
            self.comport.parity = serial.PARITY_NONE
            self.comport.stopbits = serial.STOPBITS_ONE
            self.comport.bytesize = serial.EIGHTBITS
            self.comport.close()
            self.comport.open()
            print("Link to Command Port -" + comport + "- successful")
        except serial.serialutil.SerialException as e:
            print (e)
            print("Link to Command Port -" + comport + "- failed")

        self.isInitialized = None != self.comport
        if (True == self.isInitialized):
            print("Device is ready")
        else:
            print("Device is not ready")

    def send(self,*data):
        if not self.isInitialized:
            print("Not initialized")
            return

        if not self.comport.writable():
            print("Device not writable")
            return

        buffer =  bytearray()
        for byte in data:
            if type(byte) is list:
                for subByte in byte:
                    wInput = bytearray([int(subByte)])
                    buffer.append(wInput[0])
#                    self.comport.write(wInput)
            else:
                wInput = bytearray([int(byte)])
                buffer.append(wInput[0])
#                self.comport.write(wInput)
        print("sending data : [{}]".format(buffer))

        self.comport.write(buffer)
#        self.comport.flush()
    
    def simple_protocol(self, iServoNumber, iData):
        wStartByte = 0xFF
        wServoNumberByte = int(iServoNumber)
        self.send(wStartByte, wServoNumberByte, iData)

    def polulu_protocol(self, iCommand, iServoNumber, iData):
        wStartByte = 0x80
        wDeviceByte = 0x01
        wCommandByte = int(iCommand)
        wServoNumberByte = int(iServoNumber)
        self.send(wStartByte,wDeviceByte, wCommandByte, wServoNumberByte, iData)
        
    def setRawPosition_simpleProtocol(self, iServoNumber, iPosition):
        wPosition = iPosition
        if (wPosition > 254):
            wPosition = 254
        elif (wPosition < 0):
            wPosition = 0 
        
        self.simple_protocol(iServoNumber, wPosition)


    def setPosition_simpleProtocol(self, iServoNumber, iAngle_deg):
        wAngle = iAngle_deg
        if (wAngle > 180):
            wAngle = 180
        elif (wAngle < 0):
            wAngle = 0

        wByteOne=int(254*wAngle/180)
        self.simple_protocol(iServoNumber, wByteOne)
        

    def setPosition(self, iServoNumber, iAngle_deg):
        wAngle = iAngle_deg
        if (wAngle > 180):
            wAngle = 180
        elif (wAngle < 0):
            wAngle = 0

        #Valid range is 500-5500
        wOutput=int(5000*wAngle/180+500)
        #Get the lowest 7 bits
        byteone=wOutput&127
        #Get the highest 7 bits
        bytetwo=int((wOutput-(wOutput&127))/128)
        print("byte 1 = {}, byte 2 = {}".format(byteone,bytetwo))
        self.polulu_protocol(0x04, iServoNumber, [bytetwo, byteone])


    def setSpeed(self, iServoNumber, iSpeed):
        wSpeed = iSpeed
        if (wSpeed > 127):
            wSpeed = 127
        elif (wSpeed < 0):
            wSpeed = 0
        #Get the lowest 7 bits
        byteone=int(wSpeed)
        self.polulu_protocol(0x01, iServoNumber, byteone)

def main():
    wDevice = Device("/dev/ttyAMA0", 1)
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

if "__main__":
    main()
