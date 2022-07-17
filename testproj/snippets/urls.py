from django.urls import path

from . import views

urlpatterns = [
    path('', views.SnippetList.as_view()),
    path('<int:pk>/', views.SnippetDetail.as_view()),
    path('views/<int:snippet_pk>/', views.SnippetViewerList.as_view()),
]
