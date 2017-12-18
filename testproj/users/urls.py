from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^$', views.UserList.as_view()),
    url(r'^(?P<pk>\d+)/$', views.user_detail),
]
