from django.conf.urls import url


def dummy(request):
    pass


urlpatterns = [
    url(r'^test/login$', dummy, name='login'),
    url(r'^test/logout$', dummy, name='logout'),
]
