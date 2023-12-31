from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from users.models import Subscription, User
from gen_ser.api.serializers import GenericRecipeSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Get the value indicating if the user is subscribed to the author."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.authors.filter(subscriber=request.user).exists()
        )

    class Meta:
        """Meta options for UserSerializer."""

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id')


class SubscribeUserSerializer(UserSerializer):
    """Serializer for user subscriptions."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id',
                  'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        """Get the recipes of the author."""
        recipes = obj.recipes.all()
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return GenericRecipeSerializer(recipes, many=True,
                                       read_only=True,
                                       context=self.context).data

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
        if subscriber.followers.filter(author=author).exists():
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
