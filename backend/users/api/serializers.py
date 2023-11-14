from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.api.serializers import DjoserUserSerializer, RecipeSerializer
from recipes.models import Favorite, ShoppingCart
from users.models import Subscription


class SubscribeUserSerializer(DjoserUserSerializer):
    """Serializer for user subscriptions."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        """Get the recipes of the author."""
        recipes = obj.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except Exception:
                pass
        serializer = RecipeSerializer(recipes, many=True,
                                      read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Get the count of recipes by the author."""
        return obj.recipes.count()


class PostSubscribeSerializer(serializers.ModelSerializer):
    """Serializer for creating subscriptions."""

    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')

    def validate(self, data):
        author = data.get('author')
        subscriber = data.get('subscriber')
        if subscriber.follower.filter(author=author).exists():
            raise ValidationError(
                detail='You cannot subscribe twice',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if subscriber == author:
            raise ValidationError(
                detail='You cannot subscribe to yourself',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        return SubscribeUserSerializer(
            instance.author, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite recipes."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        if self.Meta.model.objects.filter(user=data['user'],
                                          recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'You cannot add the recipe again.')
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context=self.context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Serializer for the shopping cart."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
