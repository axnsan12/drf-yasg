from django.conf.urls import url

from testproj.urls import required_urlpatterns


def dummy(request):
    pass


urlpatterns = required_urlpatterns + [
    url(r'^test/login$', dummy, name='login'),
    url(r'^test/logout$', dummy, name='logout'),
]
