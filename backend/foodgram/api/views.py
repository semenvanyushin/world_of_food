from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from django.db.models.expressions import Exists, OuterRef, Value

from .serializers import (UserGetSerializer, TokenSerializer,
                          UserPostSerializer, SetPasswordSerializer)

User = get_user_model()


class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED)


class UsersViewSet(UserViewSet):
    serializer_class = (UserGetSerializer,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.annotate(is_subscribed=Exists(
                self.request.user.follower.filter(author=OuterRef('id')))
                ).prefetch_related('follower', 'following')
        else:
            return User.objects.annotate(is_subscribed=Value(False))

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserPostSerializer
        return UserGetSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)


@api_view(['POST'])
def set_password(request):
    serializer = SetPasswordSerializer()
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль успешно изменен'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введенные данные не приняты. Ведите корректные данные.'},
        status=status.HTTP_400_BAD_REQUEST)
