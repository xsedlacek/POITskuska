from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect   
import time
import random
import math
import serial
async_mode = None

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
ser = serial.Serial('/dev/ttyACM0', 9600)

def background_thread(args):
    count = 0       
    dataList = []     
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
        time.sleep(2)    
        socketio.emit('my_response',
                      {'data': line, 'count': count},
                      namespace='/test')  
        count+=1
@app.route('/')
def hello():
    return render_template('index.html')

@socketio.on('my_event', namespace='/test')
def test_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
#    emit('my_response', {'data': 'Connected', 'count': 0})
   

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
