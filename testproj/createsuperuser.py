from __future__ import print_function

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@admin.admin'
password = 'passwordadmin'
User.objects.filter(username=username).delete()
User.objects.create_superuser(username, email, password)

print("Created superuser '%s <%s>' with password '%s'" % (username, email, password))
