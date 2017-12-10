from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_swagger import openapi
from drf_swagger.utils import swagger_auto_schema, no_body
from users.serializers import UserSerializer


class UserList(APIView):
    """UserList cbv classdoc"""

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="apiview post description override", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING)
        },
    ))
    def post(self, request):
        serializer = UserSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=no_body, operation_description="dummy operation")
    def patch(self, request):
        pass


@swagger_auto_schema(method='put', request_body=UserSerializer)
@swagger_auto_schema(methods=['get'], manual_parameters=[
    openapi.Parameter('test', openapi.IN_QUERY, "test manual param", type=openapi.TYPE_BOOLEAN),
], responses={
    200: openapi.Response('response description', UserSerializer),
})
@api_view(['GET', 'PUT'])
def user_detail(request, pk):
    """user_detail fbv docstring"""
    user = get_object_or_404(User.objects, pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)
