import os
from appCode.Common.utility import log
import hashlib

def getRtiHashAddress(iAddress, iPort):
    hash_object = hashlib.sha512("{}:{}".format(iAddress,iPort).encode("utf8"))
    hex_dig = hash_object.hexdigest()
    return int(hex_dig, 16) % (10 ** 8)

gRti_Server_Address = "localhost"
gRti_Server_Port = 9000
gRti_Participant_TimeOut = 5
gRti_Debug_Mode = False

if "RTI_SERVER_ADDRESS" in os.environ:
    gRti_Server_Address = os.environ["RTI_SERVER_ADDRESS"] 

if "RTI_SERVER_PORT" in os.environ:
    gRti_Server_Port = int(os.environ["RTI_SERVER_PORT"])

if "RTI_PARTICIPANT_TIMEOUT" in os.environ:
    gRti_Participant_TimeOut = float(os.environ["RTI_PARTICIPANT_TIMEOUT"])
    if gRti_Participant_TimeOut < 1.0:
        gRti_Participant_TimeOut = 1.0

if "RTI_DEBUG_MODE" in os.environ:
    if os.environ["RTI_DEBUG_MODE"] == str(True):
        gRti_Debug_Mode = True

gRti_Server_Hash = getRtiHashAddress(gRti_Server_Address, gRti_Server_Port)

log("RTI server address : {}:{}".format(gRti_Server_Address, gRti_Server_Port))

def getRtiServerAddress():
    return gRti_Server_Address
    
def getRtiServerPort():
    return gRti_Server_Port
    
    
def getRtiServerHash():
    return gRti_Server_Hash

def getRtiParticipantTimeOut():
    return gRti_Participant_TimeOut

    
def getRtiDebugMode():
    return gRti_Debug_Mode
