from flask import Flask, render_template, request, send_from_directory, flash, redirect, session, abort
from flask_socketio import SocketIO, send, emit
from flask_socketio import ConnectionRefusedError

import os
import socket
import sys
import threading 
import eventlet
eventlet.monkey_patch()

from appCode.Common.utility import log
from appCode.Device.database import sql

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

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


import appCode.Common.ServiceManager as ServiceManager


class WebServer(ServiceManager.Service):
    def __init__(self):
        self.mStarted = False
        self.mRunning = False
        self.mEntryPointThread = None

        wSiteDirectory = os.path.abspath('./website/')
        self.mFlaskApp = Flask(__name__, root_path=wSiteDirectory)
        self.mFlaskSocketIO = SocketIO(self.mFlaskApp)
        
    def startService(self):
        if True == self.mStarted:
            return
        log("Webserver Start")

        self.addAppRule("/", "home", home)
        self.addAppRule("/login/<path:path>", "loginSite", send_loginsite)
        self.addAppRule("/login", "login", site_login, ['POST'])
        self.addAppRule("/logout", "logout", site_logout)
        self.addAppRule("/site/<path:path>", "site", send_site)
        self.addAppRule("/script/<path:path>", "script", send_script)
        self.addAppRule("/logout", "logout", site_logout)


        self.addSocketRule('connect', socket_connect, None)
        self.addSocketRule('disconnect', socket_disconnect, None)
        self.addSocketRule('chat message', handle_chatmessage, None)
        self.addSocketRule('Broadcast TX', handle_broadcast_tx, None)


        wDatabase = sql.getDatabase('ctrlcenter')
        Base.metadata.create_all(wDatabase.getEngine())

        self.mServerThread = threading.Thread(target=self.ServerThread) 
        self.mServerThread.setDaemon(True)
        self.mServerThread.start()
      
    def ServerThread(self):
        self.mFlaskApp.secret_key = os.urandom(12)
        port = int(os.environ.get('PORT', 2000))
        self.mFlaskSocketIO.run(self.mFlaskApp, host='0.0.0.0', port=port, debug=False)

    
    def stopService(self):
        if False == self.mStarted:
            return
        log("Webserver End")
        pass

    def addAppRule(self, iEndpoint=None, iEndpoint_name=None, iHandler=None, iMethod=None):
        self.mFlaskApp.add_url_rule(iEndpoint, iEndpoint_name, iHandler, methods=iMethod)

    def addSocketRule(self, iEvent=None, iHandler=None, iNameSpace=None):
        self.mFlaskSocketIO.on_event(iEvent, iHandler, iNameSpace)


ServiceManager.initService("WebServer", True, WebServer)