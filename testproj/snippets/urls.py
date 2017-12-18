import django

from . import views

if django.VERSION[:2] >= (2, 0):
    from django.urls import path

    urlpatterns = [
        path('', views.SnippetList.as_view()),
        path('<int:pk>/', views.SnippetDetail.as_view()),
    ]
else:
    from django.conf.urls import url
    urlpatterns = [
        url('^$', views.SnippetList.as_view()),
        url(r'^(?P<pk>\d+)/$', views.SnippetDetail.as_view()),
    ]
