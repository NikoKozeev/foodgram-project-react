from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.api.serializers import UserSerializer
from recipes.models import Favorite, ShoppingCart
from gen_ser.api.serializers import GenericRecipeSerializer
from constants import MAX_AMOUNT, MIN_AMOUNT


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        """Meta options for TagSerializer."""

        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        """Meta options for IngredientSerializer."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for ingredients in a recipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Meta options for IngredientInRecipeSerializer."""

        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    ingredients = IngredientInRecipeSerializer(read_only=True, many=True,
                                               source='ingredients_in_recipe')

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.favorite_set.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shoppingcart_set.filter(recipe=obj).exists()
        )


class IngredientInRecipePostSerializer(serializers.ModelSerializer):
    """Serializer for ingredients in a recipe for POST requests."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), write_only=True
    )
    amount = IntegerField(
        max_value=MAX_AMOUNT,
        min_value=MIN_AMOUNT,
    )

    class Meta:
        """Meta options for IngredientInRecipePostSerializer."""

        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes via POST requests."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipePostSerializer(many=True)

    class Meta:
        """Meta options for RecipePostSerializer."""

        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, attrs):
        """Validate creation and modification of recipes."""
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'At least one ingredient is required'})

        ingredient_values = [ingredient['id'] for ingredient in ingredients]
        unique_ingredient_values = set(ingredient_values)

        if len(ingredient_values) != len(unique_ingredient_values):
            raise ValidationError(
                {'ingredients': 'Ingredients should not be duplicated'}
            )

        tags = attrs.get('tags')
        if not tags:
            raise ValidationError(
                {'ingredients': 'Ingredients field is not filled'}
            )
        if len(tags) != len(set(tags)):
            raise ValidationError({'tags': 'Tags should not be duplicated'})

        return attrs

    def validate_image(self, image):
        """Validate that an image is provided."""
        if not image:
            raise serializers.ValidationError({'image': 'Image is required'})
        return image

    @staticmethod
    def ingredients_amounts(ingredients, recipe):
        """Create IngredientInRecipe objects for recipe and ingredients."""
        recipe_ingredients = []
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            recipe_ingredient = IngredientInRecipe(
                ingredient=ingredient_data.get('id'),
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientInRecipe.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Create a recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **{**validated_data, **{'author': self.context['request'].user}}
        )
        recipe.tags.set(tags)
        self.ingredients_amounts(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.ingredients_amounts(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Return the created recipe to the user."""
        return RecipeSerializer(instance,
                                context=self.context).data


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
        return GenericRecipeSerializer(
            instance.recipe,
            context=self.context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Serializer for the shopping cart."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
