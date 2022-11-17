from django.shortcuts import render
import socketio
import os
import json
import time
from rest_framework.response import Response
from rest_framework import status

from threading import Thread,Condition
from django.http import HttpResponse,JsonResponse
sio = socketio.Server(async_mode='threading',cors_allowed_origins='*')
thread = None
basedir = os.path.dirname(os.path.realpath(__file__))


w=Condition()
x=Condition()
def call1(request):
    with w:
        w.wait()
    '''if request.method == 'GET':
        w.notify()
        print('GET')'''
    return JsonResponse({'key':'hi123'})
def call2(request):
    with w:
        w.notify_all()
    return JsonResponse({'key':'hi'})

global user_name
user_name = '$'
def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return HttpResponse(open(os.path.join(basedir, 'static/index.html')))
def background_thread():
    
    while True:
        sio.sleep(10)
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')

# Create your views here.
SID={'1':1,'2':2,'3':3}

lis=[]
class test_:
    
    @sio.event
    def test(sid, message):
        print('*********/*/*/*/*/*/*/')
        
        if '1' in SID:
            print('okkkkkkkkkkkkk')
            SID['2']
        else:
            print('noooooooooooo')
        if not message['data'] in lis:
            lis.append(message['data'])
        print(lis)
        print('/////////')
        sio.emit('my_response',{'data':'hiiiiiii'},room=lis)


@sio.event
def my_event(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=sid)

@sio.event
def get_name(sid, message):
    user_name=message['data']
    se = sio.get_session(sid)
    se['username']=user_name
    sio.save_session(sid,se)
    sio.emit('my_response', {'data': user_name}, room=sid)


@sio.event
def my_broadcast_event(sid, message):
    mes=message['data']
    se = sio.get_session(sid)
    
    sio.emit('my_response', {'data':se['username']+':'+mes})


@sio.event
def join(sid, message):
    sio.enter_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Entered room: ' + message['room']},
             room=sid)


@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=sid)


@sio.event
def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])


@sio.event
def my_room_(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=message['room'])
 

   

##
@sio.on('streamm')
def sss(sio,data):
    print('****************'+data)

@sio.event
def stream(sid,stream,name):
    print('++++++++++++++message'+name)
    #se = sio.get_session(sid)
    se={}
    se['stream']=stream
    se['username']=name
    #sio.save_session(sid,se)
    sio.emit('stream',se,skip_sid=sid)
    
    print('doooooooooooooooooone')

@sio.event
def connect(sid, environ):
    username ='ok'
    print('+++++++++++++connnnnected+.........'+sid)
    global count
    #count  =count+1
    #print(count)
    sio.save_session(sid, {'username': sid})
    #emit('status', {'count': count}, broadcast=True)

    #sio.emit('my_response',{'data':username}) 
##

'''@sio.event
def connection(socket):
    print('hihihhhihihihh')
    @socket.event
    def disconnect (reason):
        print(reason)
        print('reasonreasonreasonreasonreason')
        io.emit('my_response', {'data': 'disConnected'})
        sio.disconnect(sid)
    '''

@sio.event
def disconnect(sid):
    print('------------Client disconnected........'+sid)
    
    global count
    sio.emit('my_response',{'data':'disconnect_request'})
    #count =count- 1
    #emit('status', {'data': count}, broadcast=True)

# Create your views here.

