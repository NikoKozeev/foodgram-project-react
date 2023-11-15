"""Serializers."""
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.api.serializers import CustomUserSerializer


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
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        read_only=True,
        many=True,
        source='ingredients_in_recipe',
    )

    def get_is_favorited(self, obj):
        """Get whether the recipe is favorited."""
        user = self.context.get('request').user
        return user.is_authenticated and user.favorites.filter(
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Get whether the recipe is in the shopping cart."""
        user = self.context.get('request').user
        return user.is_authenticated and user.shopping_cart.filter(
            recipe=obj).exists()

    class Meta:
        """Meta options for RecipeSerializer."""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


class IngredientInRecipePostSerializer(serializers.ModelSerializer):
    """Serializer for ingredients in a recipe for POST requests."""

    id = IntegerField(write_only=True)

    class Meta:
        """Meta options for IngredientInRecipePostSerializer."""

        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes via POST requests."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipePostSerializer(many=True)

    class Meta:
        """Meta options for RecipePostSerializer."""

        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, attrs):
        """Validate creation and modification of recipes."""
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'At least one ingredient is required'})
        for ingredient in ingredients:

            value = get_object_or_404(Ingredient, id=ingredient['id'])
            if int(ingredient['amount']) < 0:
                raise ValidationError({'Invalid amount'})
            if value in ingredients_list:
                raise ValidationError({'Ingredients should not be duplicated'})
            ingredients_list.append(value)

        tags = self.initial_data.get('tags')
        tags_list = []
        if not tags:
            raise ValidationError({'Ingredients field is not filled'})
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'Tags should not be duplicated'})
            tags_list.append(tag)

        return attrs

    def validate_image(self, image):
        """Validate that an image is provided."""
        if not image:
            raise serializers.ValidationError({'Image is required'})
        return image

    def ingredients_amounts(self, ingredients, recipe):
        """Create IngredientInRecipe objects for recipe and ingredients."""
        recipe_ingredients = []
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            recipe_ingredient = IngredientInRecipe(
                ingredient_id=ingredient_data.get('id'),
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientInRecipe.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Create a recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_amounts(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.ingredients_amounts(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Return the created recipe to the user."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance,
                                context=context).data


class GenericRecipeSerializer(serializers.ModelSerializer):
    """Serializer for adding a recipe to the shopping cart."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
