from rest_framework import serializers
from datetime import datetime

from .models import useraccount, friend,notification

class getPk(serializers.Serializer):
    id=serializers.IntegerField()
    name=serializers.CharField(max_length=30)
class Userserializer(serializers.Serializer):    
    id=serializers.IntegerField()
    key=serializers.CharField(max_length=30)
    first_name=serializers.CharField(max_length=30)
    last_name=serializers.CharField(max_length=30)
    '''password=serializers.CharField(max_length=30)
    date=serializers.DateTimeField()
    email=serializers.EmailField(max_length=100)
    live=serializers.BooleanField(default=False)
    #pictcer=models.ImageField('static/image')
    account_state=serializers.BooleanField(default=True)
    key=serializers.CharField(max_length=15,default='null')'''

class notificationseralizer(serializers.Serializer):
    id=serializers.IntegerField()
    type=serializers.CharField(default='normal',max_length=30)
    is_read=serializers.BooleanField(default=False)
    time=serializers.SerializerMethodField(method_name='fullTime')
    message=serializers.CharField(default='you have a notification', max_length=155,source='content')
    sender_group=getPk()
    sender_user=Userserializer()
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
    def fullTime(self,date):
        return notificationseralizer.getTime(date.time)+' '+notificationseralizer.getdate(date.time)
    def numberNoti(self,data):
        return notification.objects.filter(user=data.user,is_read=False).count()
         
#class connectionseralizer(serializers.Serializer):
class getMemberstoMakeCallSeralizer(serializers.Serializer):
    #pk=getPk()
    #user=Userserializer()
    option=serializers.SerializerMethodField(method_name='option')
    
        
    def option():
        return{'option':{'canTallk':False,'canChat':False}}


    



