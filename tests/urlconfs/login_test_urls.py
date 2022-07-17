from django.urls import path

from testproj.urls import required_urlpatterns


def dummy(request):
    pass


urlpatterns = required_urlpatterns + [
    path('test/login', dummy, name='login'),
    path('test/logout', dummy, name='logout'),
]
