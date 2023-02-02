import io

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipePostSerilaizer, SetPasswordSerializer,
                             SubscriptionRecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             TokenSerializer, UserGetSerializer,
                             UserPostSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Subscription, Tag)

User = get_user_model()


class GetObjectMixin:
    """
    Миксин для добавления или удаления рецептов
    в избранных или списке покупок.
    """
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
    """Пользователи."""

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
    """Меняет пароль пользователя."""

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
    """Выдает список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Выдает список ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter

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

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Отдает список с ингредиентами."""

        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (request.user.shopping_cart.recipe.values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        page.setFont('Vera', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredients__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True,
                                filename='shoppingcart.pdf')
        page.setFont('Vera', 24)
        page.drawString(x_position, y_position, 'Пустой список покупок!')
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shoppingcart.pdf')


class ControlFavoriteRecipe(GetObjectMixin, generics.RetrieveDestroyAPIView,
                            generics.ListCreateAPIView):
    """Добавляет или удаляет рецепты в избранных."""

    def create(self, request, *args, **kwargs):
        isinstance = self.get_object()
        request.user.favorite_recipe.recipe.add(isinstance)
        serializer = self.get_serializer(isinstance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


class ControlShoppingCart(GetObjectMixin, generics.RetrieveDestroyAPIView,
                          generics.ListCreateAPIView):
    """Добавляет или удаляет рецепты в списке покупок."""

    def create(self, request, *args, **kwargs):
        isinstance = self.get_object()
        request.user.shopping_cart.recipe.add(isinstance)
        serializer = self.get_serializer(isinstance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


class ControlSubscription(generics.RetrieveDestroyAPIView,
                          generics.ListCreateAPIView):
    """Подписвыает или отписывает пользователя на/от автора."""

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
