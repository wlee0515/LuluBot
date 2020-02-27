import serial

class SSC03A():
    def __init__(self, comport ="/dev/ttyAMA0",timeout=1):
        self.comport = None
        self.isInitialized = False

        try:
            self.comport = serial.Serial(comport,timeout=timeout)
            self.comport.baudrate = 9600
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
            else:
                wInput = bytearray([int(byte)])
                buffer.append(wInput[0])
        print("sending data : [{}]".format(buffer))

        self.comport.write(buffer)
    
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
        

    # Pololu interface
    def setParameter(self, iServoNumber, iSetOn, iInvert, iRange):
        wRange = iRange
        if wRange > 15:
            wRange = 15
        elif wRange < 0:
            wRange = 0

        wByte = int(wRange)
        if (True == iSetOn):
            wByte = wByte&32
        if (True == iInvert):
            wByte = wByte&16
        
        self.polulu_protocol(0x00, iServoNumber, wByte)

    def setSpeed(self, iServoNumber, iSpeed):
        wSpeed = iSpeed
        if (wSpeed > 127):
            wSpeed = 127
        elif (wSpeed < 0):
            wSpeed = 0
        wByte=int(wSpeed)
        self.polulu_protocol(0x01, iServoNumber, wByte)
    
    def set7BitPosition(self, iServoNumber, iRatio):
        wRatio = iRatio
        if (wRatio > 1.0):
            wRatio = 1.0
        elif (wRatio < 0.0):
            wRatio = 0.0
        wByte=int(wRatio*127)
        self.polulu_protocol(0x02, iServoNumber, wByte)

    def set8BitPosition(self, iServoNumber, iRatio):
        wRatio = iRatio
        if (wRatio > 1.0):
            wRatio = 1.0
        elif (wRatio < 0.0):
            wRatio = 0.0
            
        #Valid range is 500-5500
        wOutput=int(wRatio*255)
        #Get the lowest 7 bits
        wByte2=wOutput&127
        #Get the highest 7 bits
        wByte1=int((wOutput-(wOutput&127))/128)
        self.polulu_protocol(0x04, iServoNumber, [wByte1, wByte2])
        
    def setPosition(self, iServoNumber, iAngle_deg):
        wAngle = iAngle_deg
        if (wAngle > 180):
            wAngle = 180
        elif (wAngle < 0):
            wAngle = 0

        #Valid range is 500-5500
        wOutput=int(5000*wAngle/180+500)
        #Get the lowest 7 bits
        wByte2=wOutput&127
        #Get the highest 7 bits
        wByte1=int((wOutput-(wOutput&127))/128)
        self.polulu_protocol(0x04, iServoNumber, [wByte1, wByte2])

    def setNeutralPosition(self, iServoNumber, iAngle_deg):
        wAngle = iAngle_deg
        if (wAngle > 180):
            wAngle = 180
        elif (wAngle < 0):
            wAngle = 0

        #Valid range is 500-5500
        wOutput=int(5000*wAngle/180+500)
        #Get the lowest 7 bits
        wByte2=wOutput&127
        #Get the highest 7 bits
        wByte1=int((wOutput-(wOutput&127))/128)
        self.polulu_protocol(0x05, iServoNumber, [wByte1, wByte2])
        
    def setServoNumberSetId(self, iServoNumberSetId):
        wSetId = iServoNumberSetId
        if (wSetId > 15):
            wSetId = 15
        elif (wSetId < 0):
            wSetId = 0
            
        #Valid range is 500-5500
        wSetId=int(wSetId)
        self.send(0xFF,0x02,wSetId)

    def checkServoNumberSetId(self):
        self.send(0xFF,0x02,0x10)
