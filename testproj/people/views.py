from rest_framework import viewsets

from .models import Identity, Person
from .serializers import IdentitySerializer, PersonSerializer


class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    queryset = Person.objects
    serializer_class = PersonSerializer


class IdentityViewSet(viewsets.ModelViewSet):
    model = Identity
    queryset = Identity.objects
    serializer_class = IdentitySerializer
