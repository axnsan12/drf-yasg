from rest_framework import viewsets
from rest_framework.pagination import BasePagination

from .models import Identity, Person
from .serializers import IdentitySerializer, PersonSerializer


class UnknownPagination(BasePagination):
    paginator_query_args = ['unknown_paginator']


class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    queryset = Person.objects
    serializer_class = PersonSerializer
    pagination_class = UnknownPagination


class IdentityViewSet(viewsets.ModelViewSet):
    model = Identity
    queryset = Identity.objects
    serializer_class = IdentitySerializer
