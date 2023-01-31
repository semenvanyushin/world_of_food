from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UsersViewSet, AuthToken, set_password,
                    TagViewSet, IngredientViewSet,
                    RecipesViewSet, ControlFavoriteRecipe,
                    ControlShoppingCart, ControlSubscription)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('users/set_password/', set_password, name='set_password'),
    path('users/<int:user_id>/subscribe',
         ControlSubscription.as_view(), name='subscribe'),
    path('recipes/<int:recipe_id>/favorite',
         ControlFavoriteRecipe.as_view(), name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart',
         ControlShoppingCart.as_view(), name='shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
