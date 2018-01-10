from __future__ import print_function

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

username = 'admin'
email = 'admin@admin.admin'
password = 'passwordadmin'

try:
    User.objects.create_superuser(username, email, password)
except IntegrityError:
    print("User '%s <%s>' already exists" % (username, email))
else:
    print("Created superuser '%s <%s>' with password '%s'" % (username, email, password))
