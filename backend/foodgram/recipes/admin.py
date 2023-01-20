from django.contrib import admin

from .models import User, Tag, Ingredient, Recipe, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined',
    )
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    list_filter = ('date_joined', 'email', 'first_name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
