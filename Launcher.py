import os, sys, subprocess, threading
from Common.utility import log, loadJSON
import json

def launchProcess(iProcess):
    log("Launching Process : {}".format(iProcess))
    process = subprocess.run(iProcess, shell=True, universal_newlines=True)
    log("Process End : {}".format(iProcess))

def main():

    wLauncherFileName = ""
    wConfigFileName = "configuration.json"
    wPhase = ""
    wPhaseCount = -1
    
    log("Session Arguments:")
    for i in range(0, len(sys.argv)):
        log("argv[{}] : {}".format(i, sys.argv[i]))
        if 0 == i:
            wLauncherFileName = sys.argv[i]
        if 1 == i:
            wConfigFileName = sys.argv[i]
        if 2 == i:
            wPhase = sys.argv[i]
        if 3 == i:
            wPhaseCount = int(sys.argv[i])

    log("Current Launch File [{}]".format(wLauncherFileName))
    log("Loading Configuration File [{}]".format(wConfigFileName))
    wConfigFile = loadJSON(wConfigFileName)
    if None == wConfigFile:
        log("Unable to load Configuration File")
        return
    else:
        log("Configuration File Loaded")
    
    if "" == wPhase:
        log("Phase not set in arguments. Searching configuration file.")
        if None == wConfigFile["startPhase"]:
            log("\"startPhase\" not defined in configuration file.")
            return
        else:
            wPhase = wConfigFile["startPhase"]
    
    log("Retrieving Current Phase Settings")
    
    if None == wConfigFile[wPhase]:
        log("Current phase, \"{}\" is not defined".format(wPhase))
        return
    
    wPhaseSetting = wConfigFile[wPhase]
    
    log("Current phase, \"{}\" definition :".format(wPhase))
    log(json.dumps(wPhaseSetting, indent=2))
    
    if 0 > wPhaseCount:
        log("Phase Count not set or badly defined. Setting phase count to 0")
        wPhaseCount = 0
    log("Current Phase Count : {}".format(wPhaseCount))
    
    if "phaseCountlimit" not in wConfigFile:
        log("\"phaseCountlimit\" limit not defined in configuration file")
        return
    else :
        if wPhaseCount > wConfigFile["phaseCountlimit"]:
            log("\"phaseCountlimit\" limit exceeded")
            return
    
    if "processList" in wPhaseSetting:
        log("Processing \"processList\"")

        wInParallel = False
        if "runParallel" in wPhaseSetting:
            log( "\"runParallel\" is defined")
            if True == wPhaseSetting["runParallel"]:
                wInParallel = True
                log( "\"runParallel\" is defined as [True]. Will run process in parallel")
            else :
                log( "\"runParallel\" is defined as [False]. Will run process sequentially")
                                
        else:
            log ("\"runParallel\" is not defined, process will execute sequentially.")
        
        if False == wInParallel:
            for wProcess in wPhaseSetting["processList"]:
                launchProcess(wProcess)
        else:
        
            wThreadList = []

            for wProcess in wPhaseSetting["processList"]:
                wThread = threading.Thread(target=launchProcess, args=(wProcess,)) 
                wThreadList.append(wThread)
            
            for wProcessThread in wThreadList:
                wProcessThread.start()

            for wProcessThread in wThreadList:
                wProcessThread.join()
                                    
    if "nextPhase" in wPhaseSetting:
        log("Starting \"nextPhase\" : \"{}\"".format(wPhaseSetting["nextPhase"]))
        launchProcess([wLauncherFileName, wConfigFileName, wPhaseSetting["nextPhase"], str(wPhaseCount+1) ])
    return


if __name__ == '__main__':
    main()
