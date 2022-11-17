
global count
count=0
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
    
    print('+++++++++++++connnnnected+.........'+sid)
    count+=1
    print(count)
    sio.save_session(sid, {'username': sid})




@sio.event
def disconnect(sid):
    count-=1
    print('------------Client disconnected........'+sid)
    print(count)
    sio.emit('my_response',{'data':'disconnect_request'})
    
# C