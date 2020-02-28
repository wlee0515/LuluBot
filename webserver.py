from flask import Flask, render_template, request, send_from_directory, flash, redirect, session, abort
from flask_socketio import SocketIO, send, emit
from flask_socketio import ConnectionRefusedError

import os
import socket
import sys
import threading 
import eventlet
eventlet.monkey_patch()

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from appCode import *
engine = create_engine('sqlite:///ctrlcenter.db', echo=True)

from Device.socket import UDPServer
from Common.utility import log

app= Flask(__name__)
socketIO = SocketIO(app)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect("/login/index.html", code=302)
        return render_template('login.html')
    else:
        return redirect("/site/home", code=302)
	
    
@app.route('/login/<path:path>')
def send_loginsite(path):
    return send_from_directory('login',path)

@app.route('/login', methods=['POST'])
def site_login():
    POST_USERNAME = str(request.json['username'])
    POST_PASSWORD = str(request.json['password'])
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        return "ERROR"
    return "TRUE"
	
@app.route("/logout")
def site_logout():
    session['logged_in'] = False
    return "TRUE"
    
@app.route('/site/<path:path>')
def send_site(path):
    if not session.get('logged_in'):
        return home()
    return send_from_directory('site', path + "/index.html")

@app.route('/script/<path:path>')
def send_script(path):
    if not session.get('logged_in'):
        return home()
    return send_from_directory('site', path)


@socketIO.on('connect')
def socket_connect():
    if not session.get('logged_in'):
        print('unauthorized client connection attempt')
        raise ConnectionRefusedError('unauthorized!')
    else:
        print('Client connected')
        emit('chat message', "Welcome")

@socketIO.on('disconnect')
def socket_disconnect():
    print('Client disconnected')

@socketIO.on('chat message')
def handle_chatmessage(message):
    print('received chat message: ' + message)
    emit('chat message', message, broadcast=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for address in mAddressList:
        sent = sock.sendto(bytes(message, 'utf8'), address)
        print('Sending data to {} port {}'.format(*address))

    sock.close()
    
@socketIO.on('Broadcast TX')
def handle_broadcast_tx(json):
    print('Broadcast message: ' + message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(bytes(json.data, 'utf8'), json.address)
    sock.close()

def Flask_Thread(arg1):
    app.secret_key = os.urandom(12)
    port = int(os.environ.get('PORT', 2000))
    
    socketIO.run(app, host='0.0.0.0', port=port, debug=False)

mAddressList = []
def UdpCallBack(iMessage, iAddress):
    if (iAddress not in mAddressList):
        mAddressList.append(iAddress)
    return socketIO.emit('chat message', iMessage, json = True, broadcast=True)


def main():	
    # creating thread 
    
    gUdpServer = UDPServer(10000, UdpCallBack)
    gUdpServer.startServer()

    wThread_Flask = threading.Thread(target=Flask_Thread, args=(None,)) 
    
    #starting thread 
    wThread_Flask.start() 
  
    # wait for thread completion
    wThread_Flask.join() 
    
    gUdpServer.stopServer()

    
    # Completion
    print("Bye!") 


if __name__ == '__main__':
    main()
