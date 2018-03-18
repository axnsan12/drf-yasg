from django.conf.urls import url

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
    url(r'^$', person_list, name='people-list'),
    url(r'^(?P<pk>[0-9]+)$', person_detail, name='person-detail'),

    url(r'^(?P<person>[0-9]+)/identity$', identity_detail,
        name='person-identity'),
)
