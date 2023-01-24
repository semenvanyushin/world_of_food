from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, AuthToken, set_password

app_name = 'api'

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UsersViewSet)

urlpatterns = [
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('users/set_password/', set_password, name='set_password'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
