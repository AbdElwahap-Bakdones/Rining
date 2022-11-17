from django.shortcuts import render
from .serializer import Userserializer,notificationseralizer,getMemberstoMakeCallSeralizer
from .models import  useraccount ,friend ,connection ,group,user_in_group,notification
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q,aggregates,Count,F
from app_ import events
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from app_ import  events
from base64 import decode,encode
from datetime import datetime
import jwt
import json
import string
import random
import base64
import time
import copy
class ClassEvents:  
    def callSendNotifEvent(keys,idNotif):
        print('idnotif')
        keyList=keys
        keyLive=useraccount.objects.filter(key__in=keyList,live=True)
        if keyLive.exists():
            events.notification.sendNoti(keyLive.values_list('key',flat=True),get_notf(idNoti=idNotif))
    #events.connection.makeCall(groupId, members, kind)
    def callMakeCallEventForLecture(groupId,admin,members):
        listMeber=[]
        members=members .filter(user__live=True,on_line=True)
        option={'canChat':'False','canTalk':'False'}
        chat=list([{'key':admin,'name':groupId.name,'message':'the first message in chat'}])
        data={'adminKey':admin,'idGroup':groupId.pk,'nameGroup':groupId.name,'kind':groupId.kind,'chat':chat}
        dicMember={}
        for m in members:
            dicMember['key']=m.user.key
            name=m.user.first_name+' '+m.user.last_name
            dicMember[m.user.key]={'key':m.user.key,'name':name,'option':option}
            listMeber.append(dicMember)
            dicMember={}
        data['member']=listMeber
        events.connection.makeCall(groupId.pk, admin, data)
        return data
    def callGroupCreatedEvent(groupInfo,keys=0):
        print('ClassEvents.callGroupCreatedEvent function')
        if keys==0:
            events.notification.groupCreated(groupInfo, groupInfo['keyMemberList'])
        else:
            events.notification.groupCreated(groupInfo, keys)
    def callmemberAddedEvent(groupId,data,membersKey):
        print('ClassEvents.callmemberAddedEvent function')
        events.notification.memberAdded(groupId, data, membersKey)
    def callEndCallEventLecture(groupId,kind):
        print('ClassEvents.callEndCallEventLecture function')
        events.connection.endCall(groupId, kind)
        print('eeennnnddd')
    def callMakeCallEventForMeeting(groupId,members,keys,keysNoAdmin,user):
        print('ClassEvents.callMakeCallEventForMeeting function')
        member={}
        for memb in members:
            member[memb.user.key]={'key':memb.user.key,'name':memb.user.first_name+' '+memb.user.last_name,'onLine':False}
        dic={'groupId':groupId.pk,'groupName':groupId.name,'kind':groupId.kind,'picture':getImage(str(groupId.picture)),'memberCount':1,'member':member}
        dic['member'][user]['onLine']=True
        events.MetingCall.makeCall(dic,keysNoAdmin,user)
    def calleventleaveCallMeeting(key,groupId):
        print('ClassEvents.calleaveCallMeeting function')
        return events.MetingCall.leaveCall(key,groupId)
    def calleventendCallForMeeting(roomId):
        print('ClassEvents.calleventendCallForMeeting Event')
        events.MetingCall.endCall(roomId)
    def callmakeCallEventForFriends(groupId,members,keys,keysNoAdmin,user):
        try:
            print('ClassEvents.callmakeCallEventForFriends')
            member={}
            for memb in members:
                print(memb)
                member[memb.user.key]={'key':memb.user.key,'name':memb.user.first_name+' '+memb.user.last_name,'onLine':False}
            dic={'groupId':groupId.pk,'groupName':groupId.name,'kind':groupId.kind,'picture':getImage(str(groupId.picture)),'memberCount':1,'member':member}
            dic['member'][user]['onLine']=True
            events.MetingCall.makeCall(dic,keysNoAdmin,user)
        except Exception as e:
            print('Error in ClassEvents.callmakeCallEventForFriends')
            print(e)
            return
#           End events        
class Group:
    def getMembers(id):
        members=user_in_group.objects.filter(group=id,active=True)
        dicMembers={}
        Admin=members.get(is_admin=True).user.key
        keyMemberList=[]
        users=useraccount.objects.filter(pk__in=members.values_list('user',flat=True))
        for user in users:
            dicMembers[user.key]={'key':user.key,'name':user.first_name,
                'live':user.live,'picture':getImage(str(user.picture))}
            keyMemberList.append(user.key)
        return {'member':dicMembers,'admin':Admin,'members_count':members.count(),'keyMemberList':keyMemberList}
    def getCall(id):
        conn=connection.objects.filter(group=id)
        count_c=1
        component_call={}
        for c in conn:
            call_duration='incall'
            if c.end_date!=None:
                call_duration=call_long(c.start_date, c.end_date)
            dic_call={'call_date':getdate(c.start_date),'call_time':getTime(c.start_date),'call_durtion':call_duration}
            component_call[count_c]=dic_call
            count_c+=1
            return component_call
    def getGruop(id):
        Group_=group.objects.get(pk=id,active=True,created=True)
        dic_group={}
        if Group_:
            member=Group.getMembers(id)
            dic_group={'id':Group_.pk,'group_name':Group_.name,
            'picture':getImage(str(Group_.picture)),'kind':Group_.kind,'members_count':member['members_count'],
            'member':member['member'],'members_count':member['members_count']-1,'calling':Group.getCall(id),'admin':member['admin'],'keyMemberList':member['keyMemberList']}
        return dic_group
        print('')
    def createGroup(name,idAdmin,keys,kind,created,picture='static/image/group/groupImage.text'):
        g=group(name=name,active=True,created=created,kind=kind,picture=picture)
        g.save()
        member=useraccount.objects.filter(key__in=keys)
        for pk in member:
            u=user_in_group(user=pk,group=g,active=True)
            u.save()
        return g.pk
#           End Group
class FriendRequest:
    def getFriendAfterAdd(id):
        data=friend.objects.get(pk=id)
        dic={}
        dic['friend_name']=data.user2.first_name
        dic['friend_lname']=data.user2.last_name
        dic['friend_email']=data.user2.email
        dic['isLive']=data.user2.live
        dic['key']=data.user2.key
        dic['check']=False
        print(dic)
        return dic
    def isUserFound(pk,key):
        print('FriendRequest.isUserFound function')
        user1=useraccount.objects.filter(pk=pk)
        user2=useraccount.objects.filter(key=key)
        if user1.exists() and user2.exists():
            return ({'state':True,'id':user2.get().pk,'user1':user1.get(),'user2':user2.get()})
            
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def accepted(user1,user2,idNotif=0):
        print('FriendRequest.accepted function')
        try:
            pk=[user1,user2]
            valid=friend.objects.filter(Q(user1__in=pk,user2__in=pk,state='accepted'))
            afriend=friend.objects.filter(user1__in=pk,user2__in=pk,state='pending')
            if afriend.count()==2 and not valid.exists():
                keyUser2=afriend.get(user2=user2).user2.key
                idUser2=afriend.get(user2=user2).pk
                idUser1=afriend.get(user1=user2).pk
                afriend.update(state='accepted')
                #events.callSendNotifEvent(afriend.get(user2=user2).user2.key, makeNotif(afriend.get(user1=user).user1.first_name+' '+afriend.get(user1=user).user1.first_name+' accepted your friend request ;)', user2))
                #events.callSendNotifEvent(afriend.get(user2=user2).user2.key, makeNotif(' accepted your friend request '+afriend.get(user1=user).user1.first_name+' '+afriend.get(user1=user).user1.first_name, user1))
                notification.objects.filter(pk=idNotif).delete()
                print(FriendRequest.getFriendAfterAdd(idUser1))
                events.notification.friendAdded(keyUser2, FriendRequest.getFriendAfterAdd(idUser1)) 
                return ({'state':True,'idNotif':idNotif,'user':FriendRequest.getFriendAfterAdd(idUser2)})
            return ({'state':False})
        except Exception as e:
            print('Error in FriendRequest.accepted function')
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def rejected(user1,user2,idNotif=0):
        try:
            print('rejected')
            pk=[user1,user2]
            state1=friend.objects.filter(user1__in=pk,user2__in=pk,state='accepted')
            state2=friend.objects.filter(user1__in=pk,user2__in=pk,state='pending')
            if state1.count()==2:
                key=state1.get(user2=user2).user2.key
                keySender=state1.get(user1=user1).user1.key
                keyReciver=state1.get(user2=user2).user2.key
                state1.update(state='rejected')
                events.notification.friendDeleted(keySender, keyReciver)
                events.notification.friendDeleted(keyReciver,keySender )
                return ({'state':True,'key':key})
            if state2.exists():
                key=state2.get(user2=user2).user1.key
                state2.update(state='rejected')
                if idNotif>0:
                    notification.objects.filter(pk=idNotif).delete()
                return ({'state':True,'key':key,'idNotif':idNotif})
            return ({'state':False})
        except Exception as e:
            print('Error in FriendRequest.rejected function')
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def addFriend(user1,Key):
        try:
            print('addFriend')
            user=FriendRequest.isUserFound(user1, Key)
            user1=user['user1']
            user2=user['user2']
            pk=[user1.pk,user2.pk]
            add=friend.objects.filter((Q(user1__in=pk,user2__in=pk))&(Q(state='accepted')|Q(state='pending')))
            print(add.exists())
            if not add.exists():
                add=friend(user1=user1,user2=user2,state='pending')
                add.save()
                add=friend(user1=user2,user2=user1,state='pending')
                add.save()
                content='you have friend request from '+add.user2.first_name+' '+add.user2.last_name
                print('end addFriend function')
                return {'state':True,'content':content,'user2':user2.pk}
            return {'state':False}
        except Exception as e:
            print('Error in FriendRequest.addFriend function')
            return Response(status=status.HTTP_400_BAD_REQUEST)
#           End FriendRequest
def getKeyLive(id):
    friend1=getKeyFriendLive(id)
    groups=user_in_group.objects.filter(user=id,active=True,group__active=True,group__created=True).values_list('group',flat=True)
    Lmember=user_in_group.objects.filter(Q(group__in=groups,group__kind='lecture',is_admin=True,user__live=True)& ~Q(user=id))
    L=Lmember.values_list('user__key',flat=True)
    Mmember=user_in_group.objects.filter(Q(group__in=groups,group__kind='Meeting',user__live=True)& ~Q(user=id))
    M=Mmember.values_list('user__key',flat=True)
    lisL=Lmember.values('group','user__key')
    lisM=Mmember.values('group','user__key')
    lis=list(L)+list(M)+list(friend1)
    groupId=list(lisL)+list(lisM)
    recever={}
    for keys in lis:
        recever[keys]=[]
    for l in groupId:
        recever[l['user__key']].append(l['group'])
    return recever  
def getKeyFriendLive(id):
    friends=friend.objects.filter(user1_id=id,state='accepted').values_list('user2',flat=True)
    user=useraccount.objects.filter(id__in=friends,live=True).values_list('key',flat=True)
    return user
def generateKey(length):
    ran = ''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase + string.digits, k = length))
    return ran
def checkToken(token):
    try:
        m= jwt.decode(token,'gra',algorithms=['HS256'])
        id=m['id']
        email=m['email']
        key=m['key']
        o=useraccount.objects.filter(email=email,key=key)
        if o.exists():
            return {'state':True,'id':id,'email':email,'key':key}
        raise Exception()
    except Exception as e:
        print('Error checkToken functions')
        print(e)
        raise Exception()
def encoderToken(id,email,key):
    return jwt.encode({'id': id,'email':email,'key':key}, 'gra', algorithm='HS256')
def insertImage(id,image,type):
    try:
        #print('insertImage function')
        path='static/'+'image/'+type+'/'+str(id)+'.txt'
        f=open(path,'w')
        f.write(image)
        return path
    except Exception as e:
        print('Error in insertImage function')
        print(e)
        return 'static/image/user/userImage.txt'
def getImage(path):
    try:
        print('getImage function')
        f = open(path, 'r')    
        return f.read()
    except Exception as e:
        print('Error in getImage function')
        print(e)
        return ''
@api_view(['POST'])
def sign_up(request):
    try:
        print('sign_up function')
        if request.method=='POST':
            print(request.data)
            firstName=request.data['firstName']
            lastName=request.data['lastName']
            password=make_password(request.data['password'])
            email=request.data['email']
            picture=''#request.data['picture']
            k=useraccount.objects.all()
            #print(firstName+' '+lastName+' '+password+' '+email)
            key=''
            if k.filter(email=email).exists():
                return Response(data={'message':'email is already used'},status=status.HTTP_406_NOT_ACCEPTABLE,)
            while True:
                key=generateKey(10)
                if not(k.filter(key=key).exists()):
                    break
            o=useraccount(first_name=firstName,last_name=lastName,password=password,email=email,key=key)
            o.save()
            '''path=insertImage(o.pk, picture, 'user')
            useraccount.objects.filter(pk=o.pk).update(picture=path)'''
            return Response({'token':encoderToken(o.pk, o.email,o.key)},status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e :
        print('Error SignUp functios')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET','POST'])
def login(request):
    token=None
    try:
        if request.method=='POST':
            email=request.data['email']
            p=request.data['password']
            user=useraccount.objects.filter(email=email)
            if user.exists() and check_password(p, user.get().password):
                return Response({'token':encoderToken(user.get().pk, user.get().email,user.get().key)},status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    except Exception as e:
        print('Error in login function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
def get_friend(id):
    friends=friend.objects.filter(user1_id=id,state='accepted')#.values('user2_id__first_name','user2_id__email')
    dic={}
    component_dic={}
    for i in friends:
        dic['friend_name']=i.user2.first_name
        dic['friend_lname']=i.user2.last_name
        dic['friend_email']=i.user2.email
        dic['isLive']=i.user2.live
        dic['key']=i.user2.key
        dic['check']=False
        dic['picture']=getImage(str(i.user2.picture))
        component_dic[i.user2.key]=dic
        dic={}
    return component_dic
def call_long(start_,end_):
    day=end_.day-start_.day
    hour=abs(end_.hour-start_.hour)
    minu=abs(end_.minute-start_.minute)
    sec=abs(end_.second-start_.second)
    durtion=day.__str__()+':'+hour.__str__()+':'+minu.__str__()+':'+sec.__str__()
    return durtion
def getdate(date):
    year=date.year
    month=date.month
    day=date.day
    hour=date.hour
    minu=date.minute
    sec=date.second
    date=year.__str__()+'/'+month.__str__()+'/'+ day.__str__()
    return date
def getTime(date):
   
    hour=date.hour
    minu=date.minute
    sec=date.second
    date=hour.__str__()+':'+minu.__str__()+':'+sec.__str__()
    return date
def deletGruop(idGruop):
    try:
        idGruop.active=False
        idGruop.save()
        return ({'state':True,'id':idGruop.pk})
    except Exception as e:
        print('Error')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
def leavGruop(userGruop):
    try:
        userGruop.active=False
        userGruop.save()
        return ({'state':True,'id':userGruop.group.pk})
    except Exception as e:
        print('Error')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
def getGroupByIdGruop(id):
    group=user_in_group.objects.filter(group_id=id,group__active=True,active=True)
    dic_member={}
    dic_group={}
    dic_call={}
    component_call={}
    component_members={}
    component_groups={}    
    count=1
    count_c=1
    if group.get():
        dic_group={'id':group.get().group.pk,'group_name':group.get().group.name,
        'photo':'photo','kind':group.get().group.kind,'members_count':all_groups.count()}
        connect=connection.objects.filter(group=group.get().group.pk)
        for x in all_groups:
            if x.is_admin:
                dic_group['admin']=x.user.key
            if not x.user.pk==id:
                dic_member={'key':x.user.key,'name':x.user.first_name,
                'live':x.user.live,'photp':'photo'}
                component_members[x.user.key]= dic_member
            
        count_c=1
        for c in connect:
            call_duration='incall'
            if c.end_date!=None:
                call_duration=call_long(c.start_date, c.end_date)
            dic_call={'call_date':getdate(c.start_date),'call_time':getTime(c.start_date),'call_durtion':call_duration}
            component_call[count_c]=dic_call
            count_c+=1

        dic_group['member']=component_members
        dic_group['calling']=component_call
        component_members={}
        component_call={}
        #print(i.group.name)
        #print(dic_group)
        component_groups[i.group.pk]=dic_group
        dic_group={}
        return component_groups
def get_group(id):
    print(id)
    group=user_in_group.objects.filter(user_id=id,group__active=True,active=True,group__created=True)
    print(group.values_list('group__name',flat=True))
    dic_member={}
    dic_group={}
    dic_call={}
    component_call={}
    component_members={}
    component_groups={}    
    count=1
    count_c=1
    for i in group:
        all_groups=user_in_group.objects.filter(group=i.group.pk,active=True)
        dic_group={'id':i.group.pk,'group_name':i.group.name,
        'picture':getImage(str(i.group.picture)),'kind':i.group.kind,'members_count':all_groups.count()}
        connect=connection.objects.filter(group=i.group.pk).filter(~Q(end_date=None)).order_by('start_date')
        for x in all_groups:
            if x.is_admin:
                dic_group['admin']=x.user.key
            if not x.user.pk==id:
                dic_member={'key':x.user.key,'name':x.user.first_name,
                'live':x.user.live,'picture':getImage(str(x.user.picture))}
                component_members[x.user.key]= dic_member
        count_c=1
        for c in connect:
            if i.group.pk==62 :
                 print(i.group.pk)
            call_duration='incall'
            if c.end_date!=None:
                call_duration=call_long(c.start_date, c.end_date)
            dic_call={'call_date':getdate(c.start_date),'call_time':getTime(c.start_date),'call_durtion':call_duration}
            component_call[count_c]=dic_call
            count_c+=1

        dic_group['member']=component_members
        dic_group['calling']=component_call
        component_members={}
        component_call={}
        #print(i.group.name)
        #print(dic_group)
        component_groups[i.group.pk]=dic_group
        dic_group={}
    return component_groups
def get_notf(idUser=0,idNoti=0):
    resu={}
    data={}
    if idUser > 0:
        notf=notification.objects.filter(user=idUser).order_by('-time')
        lis=[]
        notifdic={}
        resu['numberNotifications']=notf.filter(is_read=False).count()
        for n in notf:
            notifdic['id']=n.pk
            notifdic[n.pk]=notificationseralizer(n).data
            lis.append(notifdic)
            notifdic={}
        resu['Notifications']=lis
    elif idNoti > 0:
        notf=notification.objects.filter(pk=idNoti)
        resu['id']=notf.get().pk
        resu[notf.get().pk]=notificationseralizer(notf.get()).data
    return resu
def getMembersOnAction(idUser,idGroup):
    try:
        userGruop=user_in_group.objects.filter(Q(group=idGroup)&Q(active=True)&~Q(user=idUser)).values_list('user',flat=True)
        friend_=friend.objects.filter(Q(user1=7)&Q(state='accepted')&~Q(user2__in=userGruop)).values_list('user2',flat=True)
        user=useraccount.objects.filter(pk__in=friend_).values_list('key',flat=True)
        userL=[]
        userL=user
        return userL
    except Exception as e:
        print('Error in getMembersOnAction')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
def get_userInfo(id):
    user=useraccount.objects.get(pk=id)
    dic={}
    dic['firstName']=user.first_name
    dic['lastName']=user.last_name
    dic['email']=user.email
    dic['key']=user.key
    dic['picture']=getImage(str(user.picture))
    return dic
def makeNotif(content,idRecever,idSender=None,idConnection=None,Type='normal'):
    try:
        print('makeNotif function')
        idUser=useraccount.objects.filter(pk=idRecever)
        if Type=='normal' and idUser.exists():
            noti=notification(content=content,user=idUser.get(),type=Type)
            noti.save()
            return noti.pk
        elif Type=='call' and idUser.exists():
            idGroup=group.objects.filter(pk=idSender)
            if idGroup.exists():
                noti=notification(content=content,user=idUser.get(),sender_group=idGroup.get(),type=Type,name_sender=idGroup.get().name,connection=idConnection)
                noti.save()
                return noti.pk
        elif Type=='RAdd' and idUser.exists():
            idSend=useraccount.objects.filter(pk=idSender)
            if idSend.exists():
                noti=notification(content=content,user=idUser.get(),sender_user=idSend.get(),type=Type,name_sender=idSend.get().first_name+' '+idSend.get().last_name)
                noti.save()
                return noti.pk
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('Error in makeNotif function')
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def getUserByKeyForAdd(id,key):
    try:
        user=useraccount.objects.filter(key=key)
        Key=''
        if user.exists():
            if id == user.get().pk:
                return {'state':False,'result':user.get().first_name+' '+user.get().last_name+' (;','key':Key}
            if not friend.objects.filter( Q(user1=id) ,Q(user2=user.get().pk) , Q ( state ='accepted')|Q ( state ='pending') ):
                name=user.get().first_name+' '+user.get().last_name
                Key=user.get().key
                return ({'state':True,'result':name,'key':Key})
            if friend.objects.filter( Q(user1=id) ,Q(user2=user.get().pk) , Q ( state ='pending') ):
                return {'state':False,'result':'pending (;','key':Key}
            return {'state':False,'result':'already friend (:','key':Key}
        return {'state':False,'result':'not found ):','key':Key}
    except Exception as e:
        print('Error in function getUserByKeyForAdd')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def serchForAdd(request):
    try:
        print(request.GET)
        if request.method=='GET':
            token=checkToken(request.GET['token'])
            user=getUserByKeyForAdd(token['id'],request.GET['key'])
            return Response({'state':user['state'],'result':user['result'],'key':user['key']},status=status.HTTP_200_OK)
    except Exception as e:
        print('Error in function serchForAdd')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def addFriend(request):
    try:
        print('addFriend function')
        if request.method=='POST':
            token=checkToken(request.data['token'])
            data= FriendRequest.addFriend(token['id'], request.data['key'])
            if data['state']:
                keyList=[]
                keyList.append(request.data['key'])
                ClassEvents.callSendNotifEvent(keyList, makeNotif(content=data['content'],idRecever= data['user2'],idSender=token['id'],Type='RAdd'))
                return Response({'state':True},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in addFriend function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['GET','POST'])
def profile(request):
    pro=None
    try:
        print('profile function')
        print(request.GET)
        if request.method=='GET':
            token=checkToken(request.GET['token'])
            pro=getProfile(token['id'])
            return Response({'state':True,'profile':pro},status=status.HTTP_200_OK)
        return Response({'state':False},status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print('Error in profile function')
        print(e)
        return Response(status=status.HTTP_401_UNAUTHORIZED) 
def getProfile(id):
        dic={}
        dic['userInfo']=get_userInfo(id)
        dic['group']=get_group(id)
        dic['friend']=get_friend(id)
        dic['notifications']=get_notf(idUser=id)
        return dic
@api_view(['POST'])
def addgroup_created(request):
    try:
        print('addgroup_created function')
        if request.method=='POST':
            token=checkToken(request.data['token'])
            name_group=request.data['newGroup']['name']
            created_group=True#bool(request.data['created'])
            kind_group=request.data['newGroup']['kind']
            idSender_group=token['id']
            keys=request.data['newGroup']['members']
            if name_group!=None and type(created_group)==bool and (kind_group=='Introductory Lecture' or kind_group=='lecture' or kind_group=='Meeting')and useraccount.objects.filter(pk=idSender_group).exists(): 
                idSender=useraccount.objects.get(id=idSender_group)
                add_group=group(name=name_group,created=created_group,kind=kind_group)
                add_group.save()
                owner=group.objects.get(id=add_group.pk)
                add_owner=user_in_group(user=idSender,group=owner,is_admin='True')
                add_owner.save()
                addMemberGroup(owner.pk, keys,idSender.pk)
                groupInfo=Group.getGruop(add_group.pk)
                ClassEvents.callGroupCreatedEvent(groupInfo)
                return Response({'state':True,'data':groupInfo},status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in addgroup_created function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def statusFriend(request):
    try:
        print('statusFriend function')
        if request.method=='POST':
            print(request.data)
            token=checkToken(request.data['token'])
            idSender=token['id']
            key=request.data['key']
            stateNew=request.data['status']
            idNotif=0
            if not stateNew=='deleted':
                idNotif=request.data['notiId']
            isFound=FriendRequest.isUserFound(idSender, key)
            if isFound['state']:
                if stateNew=='rejected' or stateNew=='deleted':
                    data=FriendRequest.rejected(idSender,isFound['id'],idNotif)
                    if data['state']:
                        return Response(data,status=status.HTTP_200_OK)
                elif stateNew=='accepted':
                    data=FriendRequest.accepted(idSender, isFound['id'],idNotif)
                    if data['state']:
                        print(data)
                        return Response( data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in statusFriend function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def addMemberGroupRequest(request):
    try:
        print('addMemberGroupRequest function')
        if request.method=='POST':
            data=checkToken(request.data['token'])
            groupId=request.data['groupId']
            idUser=data['id']
            keys=request.data['keys']
            return(addMemberGroup(groupId,keys,idUser))
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in addMemberGroupRequest function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
def addMemberGroup(id_group,keys,id_admin):
        try:
            ch=False
            addedmember={}
            idGruop=group.objects.filter(pk=id_group,active=True)
            idUser=useraccount.objects.filter(pk=id_admin)
            if idGruop.exists() and idUser.exists():
                allMember=user_in_group.objects.filter(group=idGruop.get().pk,active=True)
                addKeyList=[]
                if  allMember.filter(user=idUser.get().pk,is_admin=True).exists():
                    for key in keys:
                        member=useraccount.objects.filter(key=key)
                        if member.exists():
                            returnUser={'key':key,'name':member.get().first_name+' '+member.get().last_name,'live':member.get().live,'photo':'photo'}
                            addUser=user_in_group.objects.filter(user=member.get().pk,group=idGruop.get().pk)
                            if addUser.exists():
                                if not addUser.get().active:
                                    Save=addUser.get()
                                    Save.active=True
                                    Save.save()
                                    addKeyList.append(key)
                                    addedmember[key]=returnUser
                                    content='you have added to '+idGruop.get().name+' group '
                                    idnotif=makeNotif(content=content,idRecever=member.get().pk,idSender= idGruop.get().pk)
                                    keyList=[]
                                    keyList.append(key)
                                    ClassEvents.callSendNotifEvent(keyList, idnotif)
                                    print('123')
                            else:
                                Save=user_in_group(group=idGruop.get(),user=member.get())
                                Save.save()
                                addKeyList.append(key)
                                addedmember[key]=returnUser
                                content='you have added to '+idGruop.get().name+' group '
                                idnotif=makeNotif(content=content,idRecever=member.get().pk,idSender= idGruop.get().pk)
                                keyList=[]
                                keyList.append(key)
                                ClassEvents.callSendNotifEvent(keyList, idnotif)
                    print('321')
                    ClassEvents.callGroupCreatedEvent(Group.getGruop(idGruop.get().pk),keys=addKeyList)
                    ClassEvents.callmemberAddedEvent(idGruop.get().pk, addedmember, allMember.filter(~Q(user__key__in=keys)&Q(is_admin=False)).values_list('user__key',flat=True))
                    x={'state':True,'newMembers':addedmember,'id':idGruop.get().pk,'membersKey':getMembersOnAction(id_admin, id_group)}
                    return Response(x)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                print('Error')
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def delete_group(request):
    try:
        print('API delete_group function')
        if request.method:
            data=checkToken(request.data['token'])
            groupId=request.data['id']
            idUser=data['id']
            Gruop=group.objects.filter(pk=groupId,active=True)
            user=useraccount.objects.filter(pk=idUser)
            if Gruop.exists():
                userGruop=user_in_group.objects.filter(group=Gruop.get().pk,user=user.get().pk,active=True)
                if userGruop.get().is_admin:
                    return Response(deletGruop(Gruop.get()))
                elif userGruop.exists():
                    functionReturn=leavGruop(userGruop.get())
                    if functionReturn['state']:
                        members=user_in_group.objects.filter(group=groupId,active=True).values_list('user__key',flat=True)
                        print(members)
                        events.notification.memberDeleted(groupId, user.values_list('key',flat=True), members)
                        return Response(functionReturn,status=status.HTTP_200_OK)
        return Response({'state':False})
    except Exception as e:
        print('Error in delete_group function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def delete_members(request):
    try:
        print('delete_members function')
        if request.method=='POST':
            data=checkToken(request.data['token'])
            groupId=request.data['groupId']
            idUser=data['id']
            keys=request.data['keys']
            if not type(keys)==list():
                keys=list(keys)
            isAdmin=user_in_group.objects.filter(user__pk=idUser,group__pk=groupId,group__active=True,is_admin=True,active=True)
            deletedKeys=[]
            if  isAdmin.exists():
                allMembers=user_in_group.objects.filter(group__pk=groupId)
                memberTodelete=allMembers.filter(user__key__in=keys).update(active=False)
                memberDeletedList=allMembers.filter(user__key__in=keys,active=False).values_list('user__key',flat=True)
                events.notification.memberDeleted(groupId, memberDeletedList,list(memberDeletedList)+list(allMembers.filter(active=True).values_list('user__key',flat=True)))
                return Response({'state':True,'keys':memberDeletedList,'id':groupId},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in delete_members function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def notificationRread(request):
    try:
        print('notificationRread function')
        if request.method=='POST':
            print(request.data)
            data=checkToken(request.data['token'])
            id_user=data['id']
            noti=notification.objects.filter(user=id_user,is_read=False)
            if noti.exists():
                noti.update(is_read=True)
                return Response({'state':True},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in notificationRread function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def editUserInfo(request):
    try:
        print('editUserInfo function')
        if request.method=='POST':
            data=checkToken(request.data['token'])
            id_user=data['id']
            first_name=request.data['user']['firstName']
            last_name=request.data['user']['lastName']
            password_old=request.data['user']['password']
            password_new=request.data['user']['newPassword']
            confirmPassword=request.data['user']['confirmPassword']
            picture=request.data['user']['picture']
            o=useraccount.objects.filter(id=id_user).get()
            che=False
            if o and check_password(password_old,o.password):
                if   password_new != '' and password_new==confirmPassword:
                    password_new1=make_password(password_new)
                    o.password=password_new1
                    che=True
                    print('password_new')
                if first_name!='':
                    o.first_name=first_name
                    che=True
                    print('Fname')
                if last_name!='':
                    o.last_name=last_name
                    che=True
                    print('Lname')
                if picture != None:
                    print('picture')
                    picture=insertImage(id_user, picture, 'user')
                    o.picture=picture
                    che=True
                if che:
                    o.save()
                    print('save')
                return Response({'state':True,'user':get_userInfo(o.pk)},status=status.HTTP_200_OK)
        return Response({'state':False},status=status.HTTP_400_BAD_REQUEST)  
    except Exception as e:
        print('Error in editUserInfo function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def editGroup(request):
    try:
        print('editGroup function')
        if request.method=='POST':
            data=checkToken(request.data['token'])
            if  user_in_group.objects.filter(user=data['id'] , is_admin=True).exists():
                id_group=request.data['groupId']
                name=request.data['newName']
                picture=request.data['picture']
                o=group.objects.get(id=id_group)
                che=False
                if o:
                    if name!='':
                        o.name=name
                        che=True
                    if picture!=None:
                        o.picture=insertImage(id_group, picture, 'group')
                        che=True
                    if che:
                        o.save()
                    return Response({'State':True,'id':o.pk,'name':o.name},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in editGroup function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def leave_group(reqset):
    try:
        print('API leave_group')
        if request.method=='POST':
            data=checkToken(request.data['token'])
            id_group=reqset.data['id_group']
            id_user=data['id']
            o=user_in_group.objects.filter(user=id_user,group=id_group)
            if o.exists():
                o.active=False
                o.save()
                return Response({'State':True},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in leave_group function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def makeCall(request):
    try:
        print('makeCall')
        if request.method=='POST':
            print(request.data)
            token=checkToken(request.data['token'])
            keys=request.data['keys']
            kind=request.data['kind']
            groupId1=request.data['groupId']
            groupId=group.objects.filter(pk=groupId1,active=True,created=True)
            print(groupId1)
            isInCall=connection.objects.filter(group=groupId1,end_date=None)
            if kind=='lecture' and groupId.exists() and not isInCall.exists() :
                memb=user_in_group.objects.filter(user__key__in=keys,group=groupId.get(),active=True,group__active=True)
                members=set(memb.values_list('user__key',flat=True))
                idMembers=set(memb.values_list('user__id',flat=True))
                ClassEvents.callMakeCallEventForLecture(groupId.get(),token['key'],memb)
                memb.update(on_line=True)
                conn=connection(group=groupId.get())
                conn.save()
                idNotif=0
                for pk in idMembers:
                    content='you have call from '+groupId.get().name+' group'
                    idNotif=makeNotif(content, pk,idSender=groupId.get().pk,Type='call',idConnection=conn)
                ClassEvents.callSendNotifEvent(list(members), idNotif)
                return Response({'state':True,'groupId':groupId.get().pk},status=status.HTTP_200_OK)
            elif  kind=='Meeting' and groupId.exists() and not isInCall.exists() :
                user_in_group.objects.filter(user__key=token['key'],active=True,group__pk=groupId1).update(on_line=True)
                keys.append(token['key'])
                memb=user_in_group.objects.filter(user__key__in=keys,group__pk=groupId1,active=True,group__active=True)
                keysNoAdmin=set(memb.filter(~Q(user__key=token['key'])).values_list('user__key',flat=True))
                keys=set(memb.values_list('user__key',flat=True))
                idMembers=set(memb.values_list('user__id',flat=True))
                ClassEvents.callMakeCallEventForMeeting(groupId.get(),memb,keys,keysNoAdmin,token['key'])
                conn=connection(group=groupId.get())    
                conn.save()
                #memb.update(on_line=True)
                return Response({'state':True,'groupId':groupId.get().pk},status=status.HTTP_200_OK)

            elif  kind=='Friends' and groupId1==0 and  not isInCall.exists() and keys != None:
                print('Friends')
                creator=useraccount.objects.filter(pk=token['id'])
                keys.append(token['key'])
                groupId=Group.createGroup(creator.get().first_name+' '+creator.get().last_name, token['id'], keys, kind, False,creator.get().picture)
                memb=user_in_group.objects.filter(user__key__in=keys,group__pk=groupId,active=True,group__active=True)
                members=set(memb.values_list('user__key',flat=True))
                memb.update(on_line=True)
                keysNoAdmin=set(memb.filter(~Q(user__key=token['key'])).values_list('user__key',flat=True))
                id_=group.objects.filter(pk=groupId).get()
                conn=connection(group=id_)
                conn.save()
                ClassEvents.callmakeCallEventForFriends(id_,memb,members,keysNoAdmin,token['key'])
                #here
                #if memb.exists():
                #    events.notification.sendNoti(members, get_notf(idNoti=idNotif))
                return Response({'state':True,'groupId':groupId},status=status.HTTP_200_OK)
            print('eeeeennnnnnnnddddd')
        return Response({'state':False},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in makeCall function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 
@api_view(['POST'])
def endCall(request):
    try:
        print('endCall function')
        if request.method=='POST':
            print(request.data)
            token=checkToken(request.data['token'])
            groupId=request.data['idGroup']
            kind=request.data['kind']
            user=user_in_group.objects.filter(group__pk=groupId,user__pk=token['id'],active=True,group__active=True)
            conn=connection.objects.filter(group__pk=groupId,end_date=None)
            if user.get().group.kind=='lecture' and user.get().is_admin and conn.exists() :
                conn.update(end_date=datetime.now().astimezone())
                ClassEvents.callEndCallEventLecture(groupId, kind)
                notification.objects.filter(sender_group__pk=groupId,type='call').delete()
                user_in_group.objects.filter(group__pk=groupId,active=True).update(on_line=False)
                return Response({'state':True},status=status.HTTP_200_OK)
            if  (user.get().group.kind=='Friends' or user.get().group.kind=='Meeting') and user.exists()  and conn.exists() :
                user.update(on_line=False)
                state=ClassEvents.calleventleaveCallMeeting(token['key'],groupId)                
                if state==1:
                    print('state1')
                    conn.update(end_date=datetime.now().astimezone())
                    ClassEvents.calleventendCallForMeeting(groupId)
                    members=user_in_group.objects.filter(group=groupId,on_line=True)
                    members.update(on_line=False)
                    '''for member in members:
                        print(member)
                        #id=makeNotif('The group '+user.get().group.name+' has call', member.pk)
                        #ClassEvents.callSendNotifEvent(keys, idNotif)'''
                if state==2:
                    print('state2')
                    sec=0
                    while(events.GROUPMETING[groupId]['memberCount']<=1 ):
                        sec+=5
                        time.sleep(5)
                        print(sec)
                        if events.GROUPMETING[groupId]['memberCount']>1:
                            break
                        if  sec>=30:
                            print('sec>30')
                            conn.update(end_date=datetime.now().astimezone())
                            ClassEvents.calleventendCallForMeeting(groupId)
                            user_in_group.objects.filter(group=groupId,on_line=True).update(on_line=False)
                            break
                return Response({'state':True},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('Error in endCall function')
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

x={}
#************
@api_view(['GET','POST'])
def select(request):
    try:
        
        #checkToken('eyJ0eXAiiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MywiZW1haWwiOiJyaWFkQGdtYWlsLmNvbSIsImtleSI6InBpcllub1daN24ifQ.pp01zBAA1jsO_3oKPKB0alcqQdJJg30cutTK3t0TxMo')
        noti=notification.objects.filter(type__in=['RAdd','call'])
        test=group.objects.filter(pk=2)
        allUser=useraccount.objects.all()
        m= notificationseralizer(noti,many=True)
        m=connection.objects.all()
        eventValue={'witingList':events.MetingCall.checkWitingList(5),'list':events.GROUPMETING,'SID':events.SID,'KEY':events.KEY,'GROUP':events.GROUP,'MEMBERinGROUB':events.MEMBERinGROUB,'REQUESTtalkMEMBER':events.REQUESTtalkMEMBER}
       
        
        return Response(eventValue)
    except Exception as e:
        print(e)
        return Response( status=status.HTTP_400_BAD_REQUEST)
def first(list):
    dic={}
    dic['id']=list[0]
    dic['firstName']=list[1]
    dic['lastName']=list[2]
    dic['email']=list[5]
    dic['key']=list[9]
    return dic  
#********


