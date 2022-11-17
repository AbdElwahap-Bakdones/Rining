from Accounts import views,models
from .views import sio
from functools import partial
import socketio
import json
import time
import copy
global KEY,SID
KEY={}#{sid:'key'}
SID={}#{'key':sid}
GROUP={0:{}}#{'roomId':{'adminKey':'key','idGroup':roomId,'nameGrouo':'name','kind':'kind','chat':{[{'key':admin,'name':groupId.name,'message':'the first message in chat'}]},'member':{'key':'key','name':'name','option':{'canchat':FAlse,'canTallk':False}}}}
GROUPMETING={0:{}}#{'groupId':roomId,'groupName':name,'kind':meting,'memberCount':int,'member':{key:{'key':key,'name':name,'name','onLine':bool}}}
MEMBERinGROUB={} # {'key',roomId}
REQUESTtalkMEMBER={}
class socketState:
    @sio.event
    def logIn(sid,Token):
        try:
            token=views.checkToken(Token)
            if token['key'] in SID:
                oldSid=SID[token['key']]
                connection.removMember(token['key'])
                del KEY[oldSid]
                SID[token['key']]=sid
                KEY[sid]=token['key']
                sio.disconnect(oldSid)
                print('***************************************  E-mail= '+token['email'])
            if  token['key'] in MEMBERinGROUB :
                if  MEMBERinGROUB[token['key']] in GROUPMETING :#models.user_in_group.objects.filter(user__key=token['key'],on_line=True).exists() and
                    if GROUPMETING[MEMBERinGROUB[token['key']]]['member'][token['key']]['onLine']:
                        sio.enter_room(sid,MEMBERinGROUB[token['key']])
                        DataForUser=copy.deepcopy(GROUPMETING[MEMBERinGROUB[token['key']]])
                        del DataForUser['member'][token['key']]
                        sio.emit('callJoin',DataForUser,room=sid)
                    else:
                        sio.emit('rining', GROUPMETING[MEMBERinGROUB[token['key']]],room=sid)
                elif MEMBERinGROUB[token['key']] in GROUP and GROUP[MEMBERinGROUB[token['key']]]['adminKey']==token['key'] :
                    print('callJoin after login (LECTURE)')
                    sio.enter_room(sid,MEMBERinGROUB[token['key']])
                    sio.emit('callJoin', GROUP[MEMBERinGROUB[token['key']]],  room=sid)
                
            SID[token['key']]=sid
            KEY[sid]=token['key']
            user=models.useraccount.objects.filter(key=token['key'])
            user.update(live=True)
            print('++++++++++++++Client Connected........  id= '+ str(user.get().pk)+
            ' name ='+user.get().first_name+
            ' sid= '+sid)

            notification.clientOpen(token['id'],token['key'])
            return
        except Exception as e:
            print('Error in Event socketState.logIn') 
            print(e)
            return 
    @sio.event
    def disconnect(sid):
        try:
            print('----------------------------------------')
            if  sid in KEY:
                user=models.useraccount.objects.filter(key=KEY[sid])
                connection.removMember(KEY[sid])
                del SID[KEY[sid]]
                del KEY[sid]
                user.update(live=False)
                print('------------Client disconnected........  id= '+ str(user.get().pk)+
                ' name ='+user.get().first_name+
                ' sid= '+sid)
                notification.clientClose(user.get().pk, user.get().key)
        except Exception as e:
            print('Error in socketState.disconnect')
            print(e)
            return
#   End socketState class
class notification:
    #Events
    @sio.event
    def notifRead(sid,token):
        print('Event notification.notifRead')
        try:
            token=views.checkToken(token)
            models.notification.objects.filter(user=token['id'],is_read=True).update(is_read=False)
            return
        except:
            print('Error in event notification.notifRead')
            return
    @sio.event
    def talkReques(sid,data):
        print('Event notification.activeRequest')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        print('2vmsldvkmslkmvklvmlsdkvmlksdfmv')
        key=data['key']
        result=Option.requestTalk(key, data['firstName']+' '+data['lastName'], 'pending')
        roomId=MEMBERinGROUB[key]
        Option.deleteMember(key, roomId)
        GROUP[roomId]['member'].append(result)
        REQUESTtalkMEMBER[key]='pending'
        sio.emit('requestTalk',result,room=roomId)
        sec=0
        while( key in REQUESTtalkMEMBER and REQUESTtalkMEMBER[key]=='pending' ):
            sec+=1
            if sec ==11:
                notification.stopTalk(sid, key)
                REQUESTtalkMEMBER[key]='cancel'
                return
            if key in REQUESTtalkMEMBER and REQUESTtalkMEMBER[key]=='pending':
                time.sleep(1)
                continue
            #Option.cancelRequestTalk(key)
            break
            
        return
    @sio.event
    def acceptTalk(sid,data):
        print('Event notification.talkAccepted')
        if  data['key'] in MEMBERinGROUB :
            Option.deleteMember(data['key'],MEMBERinGROUB[data['key']] )
            result=Option.requestTalk(data['key'], data['name'], 'True')
            GROUP[MEMBERinGROUB[data['key']]]['member'].append(result)
            REQUESTtalkMEMBER[data['key']]='accept'
            sio.emit('talkAccept',result,room=MEMBERinGROUB[data['key']])
    @sio.event
    def stopTalk(sid,data):
        print('Event notification.talkStop')
        if sid in KEY and KEY[sid] in MEMBERinGROUB and MEMBERinGROUB[KEY[sid]] in GROUP:
            if not data=='All':
                name=Option.deleteMember(data, MEMBERinGROUB[KEY[sid]])
                if name['state']:
                    data=Option.requestTalk(data, name['name'], 'False')
                    GROUP[MEMBERinGROUB[KEY[sid]]]['member'].append(data)
            sio.emit('talkStop',data,room=MEMBERinGROUB[KEY[sid]])
    #Functions
    def sendNoti(key,data):
        print('Event notification.sendNoti')
        sio.emit('notification',data,room=list(map(MapFunctions.getSid,key)))
    def clientOpen(id,key):
        friendsKey=views.getKeyLive(id)
        for ff in friendsKey :
            if ff in SID :
                sio.emit('clientOpen',{'key':key,'groups':friendsKey[ff]},room=SID[ff])
        return
    def clientClose(id,key):
        friendsKey=views.getKeyLive(id)
        userKey=key        
        for ff in friendsKey :
            if ff in SID :
                sio.emit('clientClose',{'key':key,'groups':friendsKey[ff]},room=SID[ff])
        return
        #print('******************* end clientClose')
        return
    def friendDeleted(keySender,keyReciver):
        print('Event notification.friendDeleted')
        if keyReciver in SID:
            sio.emit('friendDeleted',keySender,room=SID[keyReciver])
    def friendAdded(key,data):
        print('Event notification.friendAdded')
        if key in SID:
            sio.emit('friendAdded',data,room=SID[key])
            return
    def memberDeleted(groupId,deletedKey,membersKey):
        print('Event notification.memberDeleted')
        for k in membersKey:
            if k in SID:
                print(SID[k])
                print(list(deletedKey))
                print(groupId)
                sio.emit('memberDeleted',{'id':groupId,'keys':list(deletedKey)},room=SID[k])
        return
    def groupCreated(data,keys):
        print('Event notification.groupCreated ')
        for k in keys:
            if k in SID:
                sio.emit('groupCreated',{'data':data},room=SID[k])
        return
    def memberAdded(groupId,data,membersKey):
        print('Event notification.memberAdded')
        for k in membersKey:
            if k in SID:
                sio.emit('memberAdded',{'state':True,'id':groupId,'newMembers':data},room=SID[k])
    def makeCallMeeting(data,keys,user):
        try:
            print('Event notification.makeCallMeeting')

            for key in keys:
                MEMBERinGROUB[key]=data['groupId']
                if key in SID:
                    sio.emit('rining',data,room=SID[key])
                    #sio.emit('rining',data['groupId'],room=SID[key])
            if user in SID:
                MEMBERinGROUB[user]=data['groupId']
                DataForUser=copy.deepcopy(GROUPMETING[data['groupId']])
                del DataForUser['member'][KEY[SID[user]]]
                sio.enter_room(SID[user],data['groupId'])
                sio.emit('callJoin',DataForUser,room=SID[user])
                print('End Event notification.makeCallMeeting')
        except Exception as e:
            print('Error in Event notification.makeCallMeeting')
            print(e)
            return
#   End notification class
class connection:   
    # Events
    @sio.event
    def joinLecture(sid,data):
        print('Event connection.joinToCAll')
        key=data['key']
        roomId=data['groupId']
        result=Option.requestTalk(key, data['name'], 'False')
        if not SID =={} and key in SID and roomId in GROUP and not key in MEMBERinGROUB:
            MEMBERinGROUB[key]=roomId
            kind=GROUP[roomId]['kind']
            for member in GROUP[roomId]['member']:
                if member['key']==key:
                    GROUP[roomId]['member'].remove(member)
                    break
            GROUP[roomId]['member'].append(result)
            sio.enter_room(SID[key],roomId)
            sio.emit('callJoin', GROUP[roomId],  room=sid)
            data={'member':result,'kind':kind}
            sio.emit('memberJoin',data,room=roomId,skip_sid=sid)
        return
    @sio.event    
    def leaveLecture(sid,key,roomId,kind):
        print('Event connection.eventLevae')
        connection.removMember(key,roomId=roomId)        
        return   
    @sio.event
    def sendVoice(sid,data,groupId):
        print('Event connection.sendVoice')
        
        if groupId in GROUP and GROUP[groupId]['member']:
            result=''
            data=data.split(';')
            data[0]='data:video/mp4;'
            result=data[0]+data[1]
            sio.emit('reciveVoice',result,room=groupId,skip_sid=sid)
            print('++++++++++++++message')
    @sio.event
    def studentTalk(sid,data):
        print('Event notification.studentTalk')
        result=''
        if data['key'] in MEMBERinGROUB and MEMBERinGROUB[data['key']] in GROUP:
            print('talkStudent   key:'+ data['key'])
            try:
                data['sound']=data['sound'].split(';')
                data['sound'][0]='data:audio/mp3;'
                result=data['sound'][0]+data['sound'][1]
                sio.emit('talkStudent',{'sound':result,'key':data['key']},room=MEMBERinGROUB[data['key']],skip_sid=sid)
                return
            except Exceptiona as e:
                print(e)
                return 
    @sio.event
    def streamMeeting(sid,data,groupId):
        try:
            print('connection.streamMeeting Event')
            if sid in KEY and groupId in GROUPMETING and GROUPMETING[groupId]['memberCount']>1 and GROUPMETING[groupId]['member'] and KEY[sid] in GROUPMETING[groupId]['member']:
                print(GROUPMETING[groupId]['member'][KEY[sid]]['name'])
                result=''
                data=data.split(';')
                data[0]='data:video/mp4;'
                result=data[0]+data[1]
                result={'stream':result,'key':KEY[sid]}
                sio.emit('meetingStream',result,room=groupId,skip_sid=sid)
                print('++++++++++++++message')

        except Exception as e:
            print('Error in connection.streamMeeting Event')
            print(e)
            return
    # Functions
    def removMember(key,roomId=-1):
        try:
            print('Event connection.removMember')
            if key in MEMBERinGROUB and MEMBERinGROUB[key] in GROUP and  not GROUP[MEMBERinGROUB[key]]['adminKey']==key:
                roomId=MEMBERinGROUB[key]
            if roomId in GROUP:
                Option.deleteMember(key, roomId)
                kind=GROUP[roomId]['kind']
                data={'key':key,'kind':kind}
                sio.emit('memberLeave',data,room=roomId)
                sio.leave_room(SID[key],roomId)
            if key in MEMBERinGROUB and MEMBERinGROUB[key] in GROUP and   not GROUP[MEMBERinGROUB[key]]['adminKey']==key:
                del MEMBERinGROUB[key]
            return
        except Exception as e:
            print('Error in Event connection.removMember')
            print(e)
            return
    def endCall(groupId,kind):
        print('Event connection.endCall')
        sio.emit('callEnd',kind,room=groupId)
        if groupId in GROUP:
            for member in GROUP[groupId]['member']:
                del MEMBERinGROUB[member['key']]
            del MEMBERinGROUB[GROUP[groupId]['adminKey']]
            del GROUP[groupId]
    def makeCall(roomId,key,data):
            print('Event connection.makeCall (LECTURE)')
            if   not SID =={} and key in SID:
                GROUP[roomId]=data
                MEMBERinGROUB[key]=roomId
                sio.enter_room(SID[key],roomId)
                sio.emit('callJoin',data,room=SID[key])
#   End Class connection
class Option:
    def requestTalk(key,name,state):
        result={'key':key,key:{
            'key':key,
            'name':name,
            'option':{
                  'canChat':'False',
                  'canTalk': state
            }}}
        return result
    def deleteMember(key,roomId):
        try:
            if not SID =={} and key in SID and roomId in GROUP:
                for member in GROUP[roomId]['member']:
                    if member['key']==key:
                        GROUP[roomId]['member'].remove(member)
                        return {'state':True,'name':member[key]['name']}
            return {'state':False}
        except Exception as e:
            print('Error in Option.removeMember Event')
            print(e)
            return {'state':False}
    def callState():
        print('')
#   End Class Option
class MapFunctions:
    def getFriendKey(friendsKey):   
        if friendsKey in SID :
            print('in function')
            lis[userKey].append(SID[friendsKey])
        return lis[userKey]
    def enterRoom(sid):
        print('')
    def getSid(key):
        if key in SID:
            return SID[key]
    def removeAllMember(keys):
        print(keys)
        del MEMBERinGROUB[keys['key']]
#   End MapFunctions class
class Message:
    @sio.event
    def sendMessage(sid,data):
        print('Event Message.sendMessage')

        message=data['message']
        name=data['name']
        if  sid in KEY and KEY[sid] in MEMBERinGROUB and MEMBERinGROUB[KEY[sid]] in GROUP:
            roomId=MEMBERinGROUB[KEY[sid]]
            message=Message.makeMessage(KEY[sid], name, message, roomId)
            sio.emit('messageSend',message,room=roomId)
        return

    def makeMessage(key,name,message,roomId):
        message= {'key':key,'name':name,'message':message}
        GROUP[roomId]['chat'].append(message)
        return message
#   End Message class
class MetingCall:

    #   Event
    @sio.event
    def acceptMeetingCall(sid,data):
        try:
            print('MetingCall.acceptMeetingCall Event')
            if sid in KEY and KEY[sid] in data['key'] and data['groupId'] in GROUPMETING :
                memberCount=GROUPMETING[data['groupId']]['memberCount']
                GROUPMETING[data['groupId']]['memberCount']=memberCount+1
                MEMBERinGROUB[KEY[sid]]=data['groupId']
                GROUPMETING[data['groupId']]['member'][KEY[sid]]['onLine']=True
                DataForUser=copy.deepcopy( GROUPMETING[data['groupId']])
                del DataForUser['member'][KEY[sid]]
                sio.emit('callJoin',DataForUser,room=sid)
                sendKey={'member':KEY[sid],'kind':GROUPMETING[data['groupId']]['kind']}
                sio.emit('memberJoin',sendKey,room=data['groupId'])
                sio.enter_room(sid,data['groupId'])
                return              
        except Exception as e:
            print('Error in MetingCall.acceptMeetingCall Event')
            print(e)
            return
    #   function
    def makeCall(data,members,user):
        print('MetingCall.makeCall Event')
        GROUPMETING[data['groupId']]=data
        notification.makeCallMeeting(data,members,user)
    def leaveCall(key,roomId):
        try:
            print('Event MetingCall.leaveCall ')
            if key in MEMBERinGROUB and MEMBERinGROUB[key]==roomId and MEMBERinGROUB[key] in GROUPMETING and key in GROUPMETING[MEMBERinGROUB[key]]['member'] :
                memberCount=GROUPMETING[roomId]['memberCount']
                if not GROUPMETING[roomId]['member'][key]['onLine']:
                    sio.emit('clearRining',{},room=SID[key])
                    del GROUPMETING[roomId]['member'][key]
                elif GROUPMETING[roomId]['member'][key]['onLine']:
                    MetingCall.leaveMeetingMember(key,GROUPMETING[roomId]['kind'],memberCount)
                    del GROUPMETING[roomId]['member'][key]
                memberCount=GROUPMETING[roomId]['memberCount']
                if (memberCount<=1 and MetingCall.checkWitingList(roomId) == 0) or memberCount < 1:
                    return 1
                if memberCount<=1 and MetingCall.checkWitingList(roomId) >= 1:
                    return 2
                return 3
        except Exception as e:
            print('Error in Event MetingCall.leaveCall')
            print(e)
            return
    def endCall(roomId):
        print('MetingCall.endCall Event')
        if roomId in GROUPMETING:
            for key_ in GROUPMETING[roomId]['member']:
                if GROUPMETING[roomId]['member'][key_]['onLine'] and key_ in MEMBERinGROUB:
                    MetingCall.leaveMeetingMember(key_,GROUPMETING[roomId]['kind'])
                    continue
                if key_ in SID:
                    sio.emit('clearRining',{},room=SID[key_])
                if key_ in MEMBERinGROUB:
                    del MEMBERinGROUB[key_]
            del GROUPMETING[roomId]
    def leaveMeetingMember(key,kind,memberCount=0):
        GROUPMETING[MEMBERinGROUB[key]]['memberCount']=memberCount-1
        roomId=MEMBERinGROUB[key]
        del MEMBERinGROUB[key]
        #sio.emit('callEnd',kind,room=SID[key])
        sio.emit('memberLeave',{'key':key,'kind':kind},room=roomId)
        sio.leave_room(SID[key],roomId)
    def checkWitingList(roomId):
        count=0
        if not roomId in GROUPMETING:
            return 0
        for key in GROUPMETING[roomId]['member']:
            if key in MEMBERinGROUB and MEMBERinGROUB[key] == roomId and key in SID and not GROUPMETING[roomId]['member'][key]['onLine']:
                count+=1
        return count
def background_thread():
    while True:
        sio.sleep(10)
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')

'''@sio.event
    def stream(sid,data,groupId):
        print(groupId)
        if groupId in GROUP:
            sio.emit('stream',data,room=groupId,skip_sid=sid)
            print('++++++++++++++message')
    '''
