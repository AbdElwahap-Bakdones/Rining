
from django.contrib import admin
from django.urls import path,include
from  app_ import views
from . import views

urlpatterns = [
    path('',views.select ,name='select'),
    path('signup',views.sign_up ,name='sign_up'),
    path('Login',views.login,name='Login'),
    path('refreshProfile',views.profile,name='profile'),
    path('addfriend',views.addFriend,name='addfriend'),
    path('addgroup',views.addgroup_created,name='addgroup_created'),
    path('statusFriend',views.statusFriend,name='statusFriend'),
    path('addMemberGroup',views.addMemberGroupRequest,name='addMemberGroup'),
    path('delete_group',views.delete_group,name='delete_group'),
    path('deleteMember',views.delete_members,name='deleteMember'),
    path('notificationRead',views.notificationRread,name='notificationRead'),
    path('searchForAdd',views.serchForAdd,name='serchForAdd'),
    path('editUserInfo',views.editUserInfo,name='editUserInfo'),
    path('editGroup',views.editGroup,name='editGroup'),
    path('makeCall',views.makeCall,name='makeCall'),
    path('endCall',views.endCall,name='endCall'),
    



    
]