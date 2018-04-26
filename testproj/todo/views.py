from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView

from .models import Todo, TodoAnother, TodoTree, TodoYetAnother
from .serializer import TodoAnotherSerializer, TodoRecursiveSerializer, TodoSerializer, TodoTreeSerializer, \
    TodoYetAnotherSerializer


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


class NestedTodoView(RetrieveAPIView):
    serializer_class = TodoYetAnotherSerializer


class TodoTreeView(viewsets.ReadOnlyModelViewSet):
    queryset = TodoTree.objects.all()
    serializer_class = TodoTreeSerializer


class TodoRecursiveView(viewsets.ModelViewSet):
    queryset = TodoTree.objects.all()
    serializer_class = TodoRecursiveSerializer
