from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from articles import views

router = SimpleRouter()
router.register('', views.ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
