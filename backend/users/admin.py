from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin for the User model."""

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name', 'password')
    search_fields = ('email', 'username', 'first_name',
                     'last_name', 'password')
    list_filter = ('email', 'username', 'first_name', 'last_name')
    ordering = ('id',)


@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Admin for Subscriptions model."""

    list_display = ('id', 'author', 'follower')
    search_fields = ('author', 'follower')
    list_filter = ('author', 'follower')
    ordering = ('id',)
