from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'date_joined',
    )
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    list_filter = ('date_joined', 'email', 'first_name',)
    empty_value_display = '-пусто-'
