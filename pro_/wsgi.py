"""
WSGI config for pro_ project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import socketio
 
from app_.views import sio
#from app_.events import sio
#from app_.test import sio
from django.core.wsgi import get_wsgi_application
from Accounts.models import useraccount,user_in_group,connection,notification
from datetime import datetime

print('startUp ')
useraccount.objects.filter(live=True).update(live=False)
user_in_group.objects.filter(on_line=True).update(on_line=False)
connection.objects.filter(end_date=None).update(end_date=datetime.now().astimezone())
notification.objects.filter(type='call').update(type='normal')
print('start')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_.settings')

application = get_wsgi_application()
application = socketio.WSGIApp(sio, application)

