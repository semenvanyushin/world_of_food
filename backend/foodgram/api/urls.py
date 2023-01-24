from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UsersViewSet, AuthToken, set_password,
                    TagViewSet, IngredientViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('users/set_password/', set_password, name='set_password'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
