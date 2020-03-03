import os, sys, subprocess, threading
from Common.utility import log, loadJSON, loadYAML
import json

def setEvironmentVariables(oList, iSetting):
    for wkey, wVar in iSetting.items():
        oList[wkey] = "{}".format(wVar)
    
def launchProcess(iProcess):

    wCmd = []
    if "command" in iProcess:
        wCmd = iProcess["command"]
    
    wProcess_env = os.environ.copy()
    if "env" in iProcess:
        wEnv = iProcess["env"]
        setEvironmentVariables(wProcess_env, wEnv)
    
    wName = "{}".format(wCmd)
    if "Name" in iProcess:
        wName = iProcess["Name"]
        wProcess_env["ProcessName"] = wName

    log("Start Process : {}".format(wName))
    wSentCmd = []
    for wArg in wCmd:
        if "python" == wArg:
            if os.name == 'nt':
                wSentCmd.append("python")
            else:
                wSentCmd.append("python3")
        else:
            wSentCmd.append(wArg)

    log("Set cmd : {}".format(wCmd))
    log("Launching cmd : {}".format(wSentCmd))
    log("Environement : {}".format(wProcess_env))
    
    if 0 != len(wSentCmd):
        process = subprocess.Popen(wCmd, env=wProcess_env, universal_newlines=True)
    
        while None == process.poll():
            try:
                outs, errs = process.communicate()
                if None != outs:
                    log(outs)
                if None != errs:
                    log(errs)            
            except TimeoutExpired:
                pass

    log("End Process : {}".format(wName))

def main():

    wLauncherFileName = ""
    wConfigFileName = "configuration.yml"
    wPhase = ""
    wPhaseCount = -1
    wCleanEnv = os.environ.copy()
    
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

    wConfigFile = None
    if wConfigFileName.lower().endswith('.json'):
        wConfigFile = loadJSON(wConfigFileName)

    elif wConfigFileName.lower().endswith('.yml'):
        wConfigFile = loadYAML(wConfigFileName)
    else:
        log("Configuration File type not supported. Supported file types are .json and .yml")
        return

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
    
    if "env" in wConfigFile:
        wEnv = wConfigFile["env"]
        setEvironmentVariables(os.environ, wEnv)
    
    log("Retrieving Current Phase Settings")
    if None == wConfigFile[wPhase]:
        log("Current phase, \"{}\" is not defined".format(wPhase))
        return
    
    wPhaseSetting = wConfigFile[wPhase]
    
    log("Current phase, \"{}\" definition :".format(wPhase))
    log(json.dumps(wPhaseSetting, indent=2))
    
    if "env" in wPhaseSetting:
        wEnv = wPhaseSetting["env"]
        setEvironmentVariables(os.environ, wEnv)

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
        os.environ.clear()
        os.environ.update(wCleanEnv)
        log("Starting \"nextPhase\" : \"{}\"".format(wPhaseSetting["nextPhase"]))
        wNextPhase = {}
        wNextPhase["Name"] = wPhaseSetting["nextPhase"]
        wNextPhase["command"] = ["python", wLauncherFileName, wConfigFileName, wPhaseSetting["nextPhase"], str(wPhaseCount+1) ]
        launchProcess(wNextPhase)
    return


if __name__ == '__main__':
    main()
