import os, sys
import json, yaml

def saveObjAsJSON(iFileName, iObject):
    wfile = open(iFileName, "w")
    wfile.write(json.dumps(iObject, indent=4, sort_keys=True))
    wfile.close()


def loadJSON(iFileName):
    wFileHandler = open(iFileName, 'r')
    wJSONObj = None
    if 'r' == wFileHandler.mode:
        wJSONObj = json.load(wFileHandler)
    wFileHandler.close()
    return wJSONObj
    
    
def loadYAML(iFileName):
    wFileHandler = open(iFileName, 'r')
    wJSONObj = None
    if 'r' == wFileHandler.mode:
        wJSONObj = yaml.load(wFileHandler, Loader=yaml.SafeLoader)
    wFileHandler.close()
    return wJSONObj

gProcessName = None
def getProcessName():
    global gProcessName
    if None == gProcessName:
        if "ProcessName" in os.environ:
            gProcessName = os.environ["ProcessName"]
        else:
            gProcessName = os.path.basename(sys.argv[0])
    return gProcessName

def log(iLog):
    print("[{}] {}".format(getProcessName(), iLog))

def taggedInput(iMessage):
    return input("[{}] {}".format(getProcessName(), iMessage))