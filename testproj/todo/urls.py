from rest_framework import routers

from todo import views

router = routers.DefaultRouter()
router.register(r'', views.TodoViewSet)
router.register(r'another', views.TodoAnotherViewSet)
router.register(r'yetanother', views.TodoYetAnotherViewSet)

urlpatterns = router.urls
