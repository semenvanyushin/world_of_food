from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=200, unique=True, blank=False, null=False,
    )
    first_name = models.CharField(
        'имя', max_length=150, blank=False, null=False,
    )
    last_name = models.CharField(
        'фамилия', max_length=150, blank=False, null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.email
