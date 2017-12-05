from django.conf.urls import url
from django.urls import include
from rest_framework.routers import SimpleRouter

from articles import views

router = SimpleRouter()
router.register('', views.ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
