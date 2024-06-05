from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect   
import time
import random
import math
import serial
import MySQLdb 
import configparser as ConfigParser
import json

async_mode = None
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')

ser = serial.Serial('/dev/ttyACM0', 9600)
ser.baudrate = 9600
ser.reset_input_buffer()

def background_thread(args):
    count = 0       
    dataList = []
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    while True:
        print(args)
        if args:
          dbV = args.get('db_value')
        else:
          dbV = 'stop'  
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
        if dbV == 'start':
          dataDict = {
            "x": count,
            "y": int(line)
            }
          dataList.append(dataDict)
        else:
            print(str(dataList))
            if len(dataList)>0:
                fuj = str(dataList).replace("'", "\"")
                dataJsonString = json.dumps(dataList, ensure_ascii=False)
                print(dataJsonString)
                fo = open("static/files/test.txt","a+")    
                fo.write("%s\r\n" %dataJsonString)
                cursor = db.cursor()
                cursor.execute("SELECT MAX(id) FROM zadanie")
                maxid = cursor.fetchone()
                cursor.execute("INSERT INTO zadanie (id,hodnoty) VALUES (%s,%s)", (maxid[0]+1,fuj))
                db.commit()
                dataList = []
                count = 0
            print(str(dataList))
        time.sleep(2)    
        socketio.emit('my_response',
                      {'data': line, 'count': count},
                      namespace='/test')  
        count+=1
    db.close()
@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('tabs.html')

@app.route('/read/<string:num>', methods=['GET', 'POST'])
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  zadanie WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread,args=session._get_current_object())

@socketio.on('db_event', namespace='/test')
def db_message(message):
    session['db_value'] = message['value']

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
