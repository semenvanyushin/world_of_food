from django.contrib import admin

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart,
                            Subscription, Tag)


class RecipeIngredient(admin.StackedInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    list_display = ('id', 'get_author', 'name', 'text', 'cooking_time',
                    'get_tags', 'get_ingredients', 'pub_date',
                    'get_favorite_count')
    search_fields = ('name', 'cooking_time', 'author__email',
                     'ingredients__name')
    list_filter = ('name', 'author', 'pub_date', 'tags',)
    inlines = (RecipeIngredient,)
    empty_value_display = '-пусто-'

    @admin.display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Теги')
    def get_tags(self, obj):
        # return ','.join([_.name for _ in obj.tags.all()])
        return list(obj.tags.values_list('name', flat=True))

    @admin.display(description='Ингридиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipe.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', 'created',)
    search_fields = ('user__email', 'author__email',)
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe', 'get_count')
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{item["name"]} ' for item in obj.recipe.values('name')[:5]]

    @admin.display(
        description='В избранных')
    def get_count(self, obj):
        return obj.recipe.count()


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe', 'get_count')
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{item["name"]} ' for item in obj.recipe.values('name')[:5]]

    @admin.display(description='В избранных')
    def get_count(self, obj):
        return obj.recipe.count()
