from django.db import models
# Create your models here.
class useraccount(models.Model):
    first_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    password=models.CharField(max_length=255)
    date=models.DateTimeField(auto_now_add=True)
    email=models.EmailField(max_length=100)
    live=models.BooleanField(default=False)
    picture=models.ImageField(upload_to='static/image/user',default='static/image/user/userImage.txt')
    account_state=models.BooleanField(default=True)
    key=models.CharField(max_length=15,default='null')

    

class group(models.Model):
    name=models.CharField(max_length=30)
    date=models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=True)
    created=models.BooleanField(default=False)
    picture=models.ImageField(upload_to='static/image/group',default='static/image/group/groupImage.txt')
    art=[('Introductory Lecture','Introductory Lecture'),('lecture','lecture'),('Meeting','Meeting')]
    kind=models.CharField(choices=art,null=True,max_length=30)
    
class connection(models.Model):
    group=models.ForeignKey(group, on_delete=models.CASCADE)
    start_date=models.DateTimeField(auto_now_add=True)
    end_date=models.DateTimeField(null=True,blank=True)
    

class user_in_group(models.Model):
    user=models.ForeignKey(useraccount, on_delete=models.CASCADE)
    group=models.ForeignKey(group, on_delete=models.CASCADE)
    is_admin=models.BooleanField(default=False)
    active=models.BooleanField(default=True)
    on_line=models.BooleanField(default=False)
    
class friend(models.Model):
    user1=models.ForeignKey(useraccount, on_delete=models.CASCADE, related_name='user11')
    user2=models.ForeignKey(useraccount, on_delete=models.CASCADE, related_name='user22')
    art=[('accepted','accepted'),('rejected','rejected'),('pending','pending')]
    state=models.CharField(choices=art,max_length=30,default='pending')
    #start_date=models.DateTimeField(auto_now_add=True)
    #end_date=models.DateTimeField(null=True,blank=True)
    
class notification(models.Model):
    user=models.ForeignKey(useraccount, on_delete=models.CASCADE,related_name='recever')
    sender_group=models.ForeignKey(group, on_delete=models.CASCADE,null=True,blank=True)
    sender_user=models.ForeignKey(useraccount, on_delete=models.CASCADE,related_name='sender',null=True,blank=True)
    connection=models.ForeignKey(connection, on_delete=models.CASCADE,null=True,blank=True)
    type=models.CharField(default='normal',max_length=30)
    name_sender=models.CharField(default='',max_length=155)
    is_read=models.BooleanField(default=False)
    time=models.DateTimeField(auto_now_add=True)
    content=models.CharField(default='you have a notification', max_length=155)

