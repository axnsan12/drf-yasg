from rest_framework import viewsets

from .models import Todo, TodoAnother, TodoYetAnother
from .serializer import TodoAnotherSerializer, TodoSerializer, TodoYetAnotherSerializer


class TodoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'


class TodoAnotherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoAnother.objects.all()
    serializer_class = TodoAnotherSerializer


class TodoYetAnotherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoYetAnother.objects.all()
    serializer_class = TodoYetAnotherSerializer
