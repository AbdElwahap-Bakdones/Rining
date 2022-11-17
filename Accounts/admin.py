from django.contrib import admin
from .models import useraccount, group , connection , friend ,user_in_group ,notification
admin.site.register(useraccount)
admin.site.register(group)
admin.site.register(connection)
admin.site.register(friend)
admin.site.register(user_in_group)
admin.site.register(notification)

# Register your models here.
