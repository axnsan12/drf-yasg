from rest_framework import mixins, permissions, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import RetrieveAPIView

from drf_yasg.utils import swagger_auto_schema

from .models import Pack, Todo, TodoAnother, TodoTree, TodoYetAnother
from .serializer import (
    HarvestSerializer, TodoAnotherSerializer, TodoRecursiveSerializer, TodoSerializer, TodoTreeSerializer,
    TodoYetAnotherSerializer
)


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

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return TodoTreeSerializer

        raise NotImplementedError("must not call this")


class TodoRecursiveView(viewsets.ModelViewSet):
    queryset = TodoTree.objects.all()

    def get_serializer(self, *args, **kwargs):
        raise NotImplementedError("must not call this")

    def get_serializer_class(self):
        raise NotImplementedError("must not call this")

    def get_serializer_context(self):
        raise NotImplementedError("must not call this")

    @swagger_auto_schema(request_body=TodoRecursiveSerializer)
    def create(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: None, 302: 'Redirect somewhere'})
    def retrieve(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(request_body=TodoRecursiveSerializer)
    def update(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).update(request, *args, **kwargs)

    @swagger_auto_schema(request_body=TodoRecursiveSerializer)
    def partial_update(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: TodoRecursiveSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super(TodoRecursiveView, self).list(request, *args, **kwargs)


class HarvestViewSet(mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    queryset = Pack.objects.all()
    serializer_class = HarvestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def perform_update(self, serializer):
        pass
