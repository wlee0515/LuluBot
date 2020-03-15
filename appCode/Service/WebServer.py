from appCode.Common import rti
from appCode.Common.utility import log
from appCode.Common.webServer import webServer
import appCode.Common.ServiceManager as ServiceManager
from appCode.Device.database import sql


from flask import Flask, render_template, request, send_from_directory, flash, redirect, session, abort
from flask_socketio import SocketIO, send, emit
from flask_socketio import ConnectionRefusedError

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import pprint

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True)
  username = Column(String)
  password = Column(String)

  def __init__(self, username, password):
    self.username = username
    self.password = password


def home():
    if not session.get('logged_in'):
        return redirect("/login/index.html", code=302)
        return render_template('login.html')
    else:
        return redirect("/site/home", code=302)
	
def send_loginsite(path):
    return send_from_directory('login',path)

def site_login():
    print("Login Requested")
    POST_USERNAME = str(request.json['username'])
    POST_PASSWORD = str(request.json['password'])

    s = sql.getDatabase('ctrlcenter').getSesson()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    result = True
    if result:
        session['logged_in'] = True
    else:
        return "ERROR"
    return "TRUE"
	
def site_logout():
    session['logged_in'] = False
    return "TRUE"
    
def send_site(path):
    if not session.get('logged_in'):
        return home()
    return send_from_directory('site', path + "/index.html")

def send_script(path):
    if not session.get('logged_in'):
        return home()
    return send_from_directory('site', path)

def socket_connect():
    if not session.get('logged_in'):
        print('unauthorized client connection attempt')
        raise ConnectionRefusedError('unauthorized!')
    else:
        print('Client connected')
        emit('chat message', "Welcome")

def socket_disconnect():
    print('Client disconnected')

def handle_chatmessage(message):
    print('received chat message: ' + message)
    emit('chat message', message, broadcast=True)

def handle_broadcast_tx(json):
    print('Broadcast message: ' + message)

def RTI_Shutdown(path):
    if not session.get('logged_in'):
        return home()
    wNewObject = {}
    wNewObject["EndProcess"] = True
    wNewObject["target"] = path
    try:
        wNewObject["target"] = int (path)    
    except e:
        pass
    rti.getRTIEventManager("process_change").sendEvent(wNewObject)
    return "RTI End Process Event Sent"

def RTI_ShutdownAll():
    if not session.get('logged_in'):
        return home()
    wNewObject = {}
    wNewObject["EndProcess"] = True
    wNewObject["target"] = "All"
    rti.getRTIEventManager("process_change").sendEvent(wNewObject)
    return "RTI End Process Event Sent"

def RTI_LocalObject(path):
    if not session.get('logged_in'):
        return home()
    wCmd =path.split("/")
    if 2 > len(wCmd):
        wObject = rti.getRTIObjectManager(wCmd[0]).mOwnedObjects
        return pprint.pformat(wObject, indent=4)
    wObject = rti.getRTIObjectManager(wCmd[0]).getLocalObject(wCmd[1])
    return pprint.pformat(wObject, indent=4)

def RTI_RemoteObject(path):
    if not session.get('logged_in'):
        return home()
    wCmd =path.split("/")
    if 2 > len(wCmd):
        wObject = rti.getRTIObjectManager(wCmd[0]).mRemoteObjects
        return pprint.pformat(wObject, indent=4)
    wObject = rti.getRTIObjectManager(wCmd[0]).getRemoteObject(wCmd[1])
    return pprint.pformat(wObject, indent=4)

class WebServer(ServiceManager.Service):
    def __init__(self):
        self.mStarted = False
        self.mWebServer = webServer('./website/', 2000)
        
    def startService(self):
        if True == self.mStarted:
            return
        log("Webserver Start")

        self.mWebServer.addAppRule("/", "home", home)
        self.mWebServer.addAppRule("/login/<path:path>", "loginSite", send_loginsite)
        self.mWebServer.addAppRule("/login", "login", site_login, ['POST'])
        self.mWebServer.addAppRule("/logout", "logout", site_logout)
        self.mWebServer.addAppRule("/site/<path:path>", "site", send_site)
        self.mWebServer.addAppRule("/script/<path:path>", "script", send_script)
        self.mWebServer.addAppRule("/logout", "logout", site_logout)
        self.mWebServer.addAppRule("/rti/shutdown", "RTI_ShutdownAll", RTI_ShutdownAll)
        self.mWebServer.addAppRule("/rti/shutdown/<path:path>", "RTI_Shutdown", RTI_Shutdown)
        self.mWebServer.addAppRule("/rti/object/local/<path:path>", "RTI_Obj_local", RTI_LocalObject)
        self.mWebServer.addAppRule("/rti/object/remote/<path:path>", "RTI_Obj_remote", RTI_RemoteObject)
        
        self.mWebServer.addSocketRule('connect', socket_connect, None)
        self.mWebServer.addSocketRule('disconnect', socket_disconnect, None)
        self.mWebServer.addSocketRule('chat message', handle_chatmessage, None)
        self.mWebServer.addSocketRule('Broadcast TX', handle_broadcast_tx, None)

        self.mWebServer.startServer()
        wDatabase = sql.getDatabase('ctrlcenter')
        Base.metadata.create_all(wDatabase.getEngine())

      
    def stopService(self):
        if False == self.mStarted:
            return
        log("Webserver End")
        pass



ServiceManager.initService("LuluBotWebServer", True, WebServer)