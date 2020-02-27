import os
import subprocess
import Common.utility as utility
import sys
import json

def launchProcess(iProcess):
    wStdOutMode = subprocess.PIPE
    if "start" == iProcess[0]:
        wStdOutMode = subprocess.DEVNULL
    wFromShell = True
    out = subprocess.Popen(
        iProcess, 
        stdout=wStdOutMode, 
        stderr=subprocess.STDOUT,
        shell=wFromShell)

    wStdOut, wStdErr = out.communicate()

    if None != wStdOut:
        print(wStdOut.decode("utf-8"))
    
    if None != wStdErr:
        print(wStdErr.decode("utf-8"))

def main():

    wLauncherFileName = ""
    wConfigFileName = "configuration.json"
    wPhase = ""
    wPhaseCount = -1
    
    print("Session Arguments:")
    for i in range(0, len(sys.argv)):
        print("argv[{}] : {}".format(i, sys.argv[i]))
        if 0 == i:
            wLauncherFileName = sys.argv[i]
        if 1 == i:
            wConfigFileName = sys.argv[i]
        if 2 == i:
            wPhase = sys.argv[i]
        if 3 == i:
            wPhaseCount = int(sys.argv[i])

    print("Current Launch File [{}]".format(wLauncherFileName))
    print("Loading Configuration File [{}]".format(wConfigFileName))
    wConfigFile = utility.loadJSON(wConfigFileName)
    if None == wConfigFile:
        print("Unable to load Configuration File")
        return
    else:
        print("Configuration File Loaded")
    
    if "" == wPhase:
        print("Phase not set in arguments. Searching configuration file.")
        if None == wConfigFile["startPhase"]:
            print("\"startPhase\" not defined in configuration file.")
            return
        else:
            wPhase = wConfigFile["startPhase"]
    
    print("Retrieving Current Phase Settings")
    
    if None == wConfigFile[wPhase]:
        print("Current phase, \"{}\" is not defined".format(wPhase))
        return
    
    wPhaseSetting = wConfigFile[wPhase]
    
    print("Current phase, \"{}\" definition :".format(wPhase))
    print(json.dumps(wPhaseSetting, indent=2))
    
    if 0 > wPhaseCount:
        print("Phase Count not set or badly defined. Setting phase count to 0")
        wPhaseCount = 0
    print("Current Phase Count : {}".format(wPhaseCount))
    
    if "phaseCountlimit" not in wConfigFile:
        print("\"phaseCountlimit\" limit not defined in configuration file")
        return
    else :
        if wPhaseCount > wConfigFile["phaseCountlimit"]:
            print("\"phaseCountlimit\" limit exceeded")
            return
    
    if "processList" in wPhaseSetting:
        print("Processing \"processList\"")
        for wProcess in wPhaseSetting["processList"]:
            launchProcess(wProcess)
            
    if "nextPhase" in wPhaseSetting:
        print("Starting \"nextPhase\" : \"{}\"".format(wPhaseSetting["nextPhase"]))
        launchProcess([wLauncherFileName, wConfigFileName, wPhaseSetting["nextPhase"], str(wPhaseCount+1) ])
    return


if __name__ == '__main__':
    main()