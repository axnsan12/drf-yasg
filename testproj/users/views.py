from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from users.serializers import UserListQuerySerializer, UserSerializer


class UserList(APIView):
    """UserList cbv classdoc"""

    @swagger_auto_schema(
        query_serializer=UserListQuerySerializer,
        responses={200: UserSerializer(many=True)},
        tags=['Users'],
    )
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="apiview post description override",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING)
            },
        ),
        security=[],
        tags=['Users'],
    )
    def post(self, request):
        serializer = UserSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_id="users_dummy", operation_description="dummy operation", tags=['Users'])
    def patch(self, request):
        pass


@swagger_auto_schema(method='put', request_body=UserSerializer, tags=['Users'])
@swagger_auto_schema(methods=['get'], manual_parameters=[
    openapi.Parameter('test', openapi.IN_QUERY, "test manual param", type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('test_array', openapi.IN_QUERY, "test query array arg", type=openapi.TYPE_ARRAY,
                      items=openapi.Items(type=openapi.TYPE_STRING), required=True, collection_format='multi'),
], responses={
    200: openapi.Response('response description', UserSerializer),
}, tags=['Users'])
@api_view(['GET', 'PUT'])
def user_detail(request, pk):
    """user_detail fbv docstring"""
    user = get_object_or_404(User.objects, pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)


class DummyAutoSchema:
    def __init__(self, *args, **kwargs):
        pass

    def get_operation(self, keys):
        pass


@swagger_auto_schema(methods=['get'], auto_schema=DummyAutoSchema)
@swagger_auto_schema(methods=['PUT'], auto_schema=None)
@api_view(['GET', 'PUT'])
def test_view_with_dummy_schema(request, pk):
    return Response({})
