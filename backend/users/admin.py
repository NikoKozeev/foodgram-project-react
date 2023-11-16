from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for the User model."""

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name', 'recipes_count', 'subscriber_count')
    search_fields = ('email', 'username', 'first_name',
                     'last_name')
    list_filter = ('email', 'username', 'first_name', 'last_name')
    ordering = ('id',)

    @admin.display(description='recipes count')
    def recipes_count(self, obj):
        """Return number of recipes."""
        return obj.recipes.count()

    @admin.display(description='subscriber count')
    def subscriber_count(self, obj):
        """Return number of subscribers."""
        return obj.author.count()


@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Admin for Subscriptions model."""

    list_display = ('id', 'author', 'subscriber')
    search_fields = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    ordering = ('id',)
