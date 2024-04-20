from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import serial

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
ser = serial.Serial('/dev/ttyACM0', 9600)  # Nastav sériový port, uprav podľa potreby

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_monitoring', namespace='/test')
def handle_start_monitoring():
    ser.write(b'M')  # Poslať príkaz na začatie monitorovania
    
@socketio.on('start_control', namespace='/test')
def handle_start_control(value):
    ser.write(b'R')
    brightness_value = int(value)
    ser.write(brightness_value.to_bytes(1, byteorder='big'))  # Poslať hodnotu jasu cez sériový port
@socketio.on('brightness_control')
def handle_brightness_control(value):
    brightness_value = int(value)
    ser.write(brightness_value.to_bytes(1, byteorder='big'))  # Poslať hodnotu jasu cez sériový port
@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
