from rest_framework import serializers
from django.contrib.auth import authenticate
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password

from users.models import User
from .mixins import GetIsSubscribedMixin

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
