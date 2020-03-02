import os
from Common.utility import log

gRti_Server_Address = "localhost"
gRti_Server_Port = 9000
gRti_Participant_TimeOut = 5

if "RTI_SERVER_ADDRESS" in os.environ:
    gRti_Server_Address = os.environ["RTI_SERVER_ADDRESS"] 

if "RTI_SERVER_PORT" in os.environ:
    gRti_Server_Port = int(os.environ["RTI_SERVER_PORT"])

if "RTI_PARTICIPANT_TIMEOUT" in os.environ:
    gRti_Participant_TimeOut = float(os.environ["RTI_PARTICIPANT_TIMEOUT"])
    if gRti_Participant_TimeOut < 1.0:
        gRti_Participant_TimeOut = 1.0

log("RTI server address : {}:{}".format(gRti_Server_Address, gRti_Server_Port))

def getRtiServerAddress():
    return gRti_Server_Address
    
def getRtiServerPort():
    return gRti_Server_Port
    
def getRtiParticipantTimeOut():
    return gRti_Participant_TimeOut
