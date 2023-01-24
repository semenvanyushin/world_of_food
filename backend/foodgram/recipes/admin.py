from django.contrib import admin

from .models import Tag, Ingredient, Recipe, Subscription


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'image', 'text', 'cooking_time',)
    search_fields = ('name',)
    list_filter = ('author', 'name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
