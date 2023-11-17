from rest_framework import serializers

from recipes.models import Recipe


class GenericRecipeSerializer(serializers.ModelSerializer):
    """Serializer for adding a recipe to the shopping cart."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
