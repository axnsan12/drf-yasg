from django.urls import include, path
from rest_framework.routers import SimpleRouter

from articles import views

router = SimpleRouter()
router.register('', views.ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
