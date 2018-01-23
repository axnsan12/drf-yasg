from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from users.serializers import UserListQuerySerializer, UserSerializerrr


class UserList(APIView):
    """UserList cbv classdoc"""

    @swagger_auto_schema(query_serializer=UserListQuerySerializer, responses={200: UserSerializerrr(many=True)})
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
        security=[]
    )
    def post(self, request):
        serializer = UserSerializerrr(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=no_body, operation_id="users_dummy", operation_description="dummy operation")
    def patch(self, request):
        pass


@swagger_auto_schema(method='put', request_body=UserSerializerrr)
@swagger_auto_schema(methods=['get'], manual_parameters=[
    openapi.Parameter('test', openapi.IN_QUERY, "test manual param", type=openapi.TYPE_BOOLEAN),
], responses={
    200: openapi.Response('response description', UserSerializerrr),
})
@api_view(['GET', 'PUT'])
def user_detail(request, pk):
    """user_detail fbv docstring"""
    user = get_object_or_404(User.objects, pk=pk)
    serializer = UserSerializerrr(user)
    return Response(serializer.data)
