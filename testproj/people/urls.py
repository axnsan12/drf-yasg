from django.urls import path

from .views import IdentityViewSet, PersonViewSet

person_list = PersonViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
person_detail = PersonViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

identity_detail = IdentityViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

urlpatterns = (
    path('', person_list, name='people-list'),
    path('<int:pk>', person_detail, name='person-detail'),

    path('<int:person>/identity', identity_detail,
         name='person-identity'),
)
