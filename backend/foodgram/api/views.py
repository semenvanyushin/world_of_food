from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        SAFE_METHODS,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.decorators import api_view, action
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status, viewsets, generics
from django.db.models.expressions import Exists, OuterRef, Value

from .serializers import (UserGetSerializer, TokenSerializer,
                          UserPostSerializer, SetPasswordSerializer,
                          TagSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerilaizer,
                          SubscriptionSerializer, SubscriptionRecipeSerializer)
from recipes.models import (Tag, Ingredient, Recipe, FavoriteRecipe,
                            ShoppingCart, Subscription)
from .permissions import IsAdminOrReadOnly

User = get_user_model()


class GetObjectMixin:
    serializer_class = SubscriptionRecipeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


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

    @action(permission_classes=(IsAuthenticated,), detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(FavoriteRecipe.objects.filter(
                    user=self.request.user, recipe=OuterRef('id'))),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user=self.request.user, recipe=OuterRef('id')))
                ).select_related('author').prefetch_related(
                    'tags', 'ingredients', 'recipe',
                    'shopping_cart', 'favorite_recipe')
        else:
            return Recipe.objects.annotate(
                is_favorited=Value(False),
                is_in_shopping_cart=Value(False)
                ).select_related('author').prefetch_related(
                    'tags', 'ingredients', 'recipe',
                    'shopping_cart', 'favorite_recipe')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerilaizer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ControlFavoriteRecipe(GetObjectMixin, generics.RetrieveDestroyAPIView,
                            generics.ListCreateAPIView):

    def create(self, request, *args, **kwargs):
        isinstance = self.get_object()
        request.user.favorite_recipe.recipe.add(isinstance)
        serializer = self.get_serializer(isinstance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


class ControlShoppingCart(GetObjectMixin, generics.RetrieveDestroyAPIView,
                          generics.ListCreateAPIView):

    def create(self, request, *args, **kwargs):
        isinstance = self.get_object()
        request.user.shopping_cart.recipe.add(isinstance)
        serializer = self.get_serializer(isinstance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


class ControlSubscription(generics.RetrieveDestroyAPIView,
                          generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following').prefetch_related('folliwing__recipe').annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),)

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response({'errors': 'Невозможно подписаться на себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe = request.user.follower.create(author=instance)
        serilizer = self.get_serializer(subscribe)
        return Response(serilizer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.follower.filter(author=instance).delete()
