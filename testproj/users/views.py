from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from users.serializers import UserListQuerySerializer, UserSerializerrr


class UserList(APIView):
    """UserList cbv classdoc"""

    @swagger_auto_schema(
        query_serializer=UserListQuerySerializer,
        responses={200: UserSerializerrr(many=True)},
        tags=['Users'],
    )
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserSerializerrr(queryset, many=True)
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
        serializer = UserSerializerrr(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_id="users_dummy", operation_description="dummy operation", tags=['Users'])
    def patch(self, request):
        pass


@swagger_auto_schema(method='put', request_body=UserSerializerrr, tags=['Users'])
@swagger_auto_schema(methods=['get'], manual_parameters=[
    openapi.Parameter('test', openapi.IN_QUERY, "test manual param", type=openapi.TYPE_BOOLEAN),
    openapi.Parameter('test_array', openapi.IN_QUERY, "test query array arg", type=openapi.TYPE_ARRAY,
                      items=openapi.Items(type=openapi.TYPE_STRING), required=True, collection_format='multi'),
], responses={
    200: openapi.Response('response description', UserSerializerrr),
}, tags=['Users'])
@api_view(['GET', 'PUT'])
def user_detail(request, pk):
    """user_detail fbv docstring"""
    user = get_object_or_404(User.objects, pk=pk)
    serializer = UserSerializerrr(user)
    return Response(serializer.data)
