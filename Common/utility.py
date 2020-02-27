import json
import yaml

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
        wJSONObj = yaml.load(wFileHandler)
    wFileHandler.close()
    return wJSONObj