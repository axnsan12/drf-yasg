from django.urls import path

from users import views

urlpatterns = [
    path('', views.UserList.as_view()),
    path('<int:pk>/', views.user_detail),
    path('<int:pk>/test_dummy', views.test_view_with_dummy_schema),
]
