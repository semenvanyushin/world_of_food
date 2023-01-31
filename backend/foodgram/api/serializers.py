from rest_framework import serializers
from django.contrib.auth import authenticate
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password
from drf_base64.fields import Base64ImageField

from users.models import User
from .mixins import GetIsSubscribedMixin
from recipes.models import (Tag, Ingredient, Recipe, Subscription,
                            RecipeIngredient)

auth_error = 'Не удается войти в систему с предоставленными учетными данными.'


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(label='Email', write_only=True)
    password = serializers.CharField(
        label='Пароль', style={'input_type': 'password'},
        trim_whitespace=False, write_only=True)
    token = serializers.CharField(label='Токен', read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    auth_error, code='authorization')
        else:
            raise serializers.ValidationError(
                'Не указаны Email и Пароль', code='authorization')
        attrs['user'] = user
        return attrs


class UserGetSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)


class UserPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password',)

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(username=user.email, password=current_password):
            raise serializers.ValidationError(
                auth_error, code='authtorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.PasswordValidator(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientPatchSerilizer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeUserSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = RecipeUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source='recipe')
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')


class RecipePostSerilaizer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientPatchSerilizer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_field = ('author',)


class SubscriptionRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = obj.author.recipe.all()[:int(limit)]
        else:
            recipes = obj.author.recipe.all()
        return SubscriptionRecipeSerializer(recipes, many=True).data
