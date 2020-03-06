from flask import Flask
from flask_socketio import SocketIO

import os
import threading 
import eventlet
eventlet.monkey_patch()


class webServer:
    def __init__(self, iWebSiteFolder, iPort):
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None

        self.mDirectory = os.path.abspath('./{}/'.format(iWebSiteFolder))
        self.mPort = iPort
        self.mFlaskApp = None
        self.mFlaskSocketIO = None
        
    def startServer(self):
        if True == self.mStarted:
            return
        self.mServerThread = threading.Thread(target=self.ServerThread) 
        self.mServerThread.setDaemon(True)
        self.mServerThread.start()
      
    def ServerThread(self):
        self.mFlaskApp.secret_key = os.urandom(12)
        port = int(os.environ.get('PORT', self.mPort))
        print ("running on port {}".format(self.mPort))
        self.mFlaskSocketIO.run(self.mFlaskApp, host='0.0.0.0', port=port, debug=False)

    def addAppRule(self, iEndpoint=None, iEndpoint_name=None, iHandler=None, iMethod=None):
        if None == self.mFlaskApp:
            self.mFlaskApp = Flask(__name__, root_path=self.mDirectory)
        self.mFlaskApp.add_url_rule(iEndpoint, iEndpoint_name, iHandler, methods=iMethod)

    def addSocketRule(self, iEvent=None, iHandler=None, iNameSpace=None):
        if None == self.mFlaskSocketIO:
            if None == self.mFlaskApp:
                self.mFlaskApp = Flask(__name__, root_path=self.mDirectory)
            self.mFlaskSocketIO = SocketIO(self.mFlaskApp)
        self.mFlaskSocketIO.on_event(iEvent, iHandler, iNameSpace)