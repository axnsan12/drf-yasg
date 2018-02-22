from rest_framework import viewsets

from .models import Todo, TodoAnother, TodoYetAnother
from .serializer import TodoAnotherSerializer, TodoSerializer, TodoYetAnotherSerializer


class TodoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class TodoAnotherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoAnother.objects.all()
    serializer_class = TodoAnotherSerializer


class TodoYetAnotherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoYetAnother.objects.all()
    serializer_class = TodoYetAnotherSerializer
