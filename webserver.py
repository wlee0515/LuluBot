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


app = Flask(__name__)
socketio = SocketIO(app)

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
    
@app.route("/adduser")
def site_adduser():
    POST_USERNAME = str(request.json['username'])
    POST_PASSWORD = str(request.json['password'])
    
    POST_NEW_USERNAME = str(request.json['new_user'])
    POST_NEW_USER_PASSWORD = str(request.json['new_user_password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        query = s.query(User).filter(User.username.in_([POST_NEW_USERNAME]), User.password.in_([POST_NEW_USER_PASSWORD]) )
        result2 = query.first()
        
        if result2:
            return "ERROR : Username Already Exist"
    else:
        return "ERROR : Endorser not found"

    user = User(POST_NEW_USERNAME, POST_NEW_USER_PASSWORD)
    session.add(user)
    session.commit()

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

@app.route('/time')
def send_time():
    if not session.get('logged_in'):
        return home()
    return time.strftime("%A, %d. %B %Y %I:%M:%S %p")
	
@socketio.on('connect')
def socket_connect():
    if not session.get('logged_in'):
        print('unauthorized client connection attempt')
        raise ConnectionRefusedError('unauthorized!')
    else:
        print('Client connected')
        emit('chat message', "Welcome")

@socketio.on('disconnect')
def socket_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    send(json, json=True)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('my response', json)

@socketio.on('my event 1')
def handle_my_custom_event(arg1, arg2, arg3):
    print('received args: ' + arg1 + arg2 + arg3)
    send(message, namespace='/chat')

@socketio.on('my event 2', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
    emit('my response', ('foo', 'bar', json), namespace='/chat')

@socketio.on('my event 3', namespace='/test')
def handle_my_custom_namespace_event2(json):
    print('received json: ' + str(json))
    return 'one', 2

def my_function_handler(data):
    pass
socketio.on_event('my event 4', my_function_handler, namespace='/test')


@socketio.on('chat message')
def handle_chatmessage(message):
    print('received chat message: ' + message)
    emit('chat message', message, broadcast=True)
    

@socketio.on('Broadcast TX')
def handle_broadcast_tx(json):
    print('Broadcast message: ' + message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(bytes(json.data, 'utf8'), json.address)
    sock.close()


def ack():
    print("message was received!")

ShutdownFlag = False

def Flask_Thread(arg1):
    app.secret_key = os.urandom(12)
    port = int(os.environ.get('PORT', 2000))
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
    ShutdownFlag = True


def UDP_Receive_Thread(arg1):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    sock.settimeout(1)
    while False == ShutdownFlag:
        print('\nwaiting to receive message')
        try:
            data, address = sock.recvfrom(4096)
            print('received {} bytes from {}'.format(len(data), address))
            print(data)
            if data:    
                NewMessage = {}
                NewMessage["data"] = data.decode("utf-8")
                NewMessage["address"] = address
#                socketio.emit('chat message', data.decode("utf-8"), broadcast=True)
                socketio.emit('chat message', NewMessage, json = True, broadcast=True)
                sent = sock.sendto(data, address)
                print('sent {} bytes back to {}'.format(sent, address))
        except socket.timeout as e:
            print(e)


def main():	
    # creating thread 
    wThread_Flask = threading.Thread(target=Flask_Thread, args=(None,)) 
    wThread_UDP_RX = threading.Thread(target=UDP_Receive_Thread, args=(None,)) 
    
    #starting thread 
    wThread_Flask.start() 
    wThread_UDP_RX.start()
  
    # wait for thread completion
    wThread_Flask.join() 
    wThread_UDP_RX.join() 

    # Completion
    print("Bye!") 


if __name__ == '__main__':
    main()
