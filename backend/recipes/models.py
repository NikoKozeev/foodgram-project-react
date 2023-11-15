"""Module for Django models used in the recipes app."""
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(
        verbose_name='Name',
        max_length=254,
        blank=False,
        unique=True,
        null=False
    )
    color = models.CharField(
        'Color',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Value is not a valid color in HEX format!'
            )
        ],
        default='#00cc00',
        help_text='Enter the tag color. HEX format: ##00cc00',
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=254,
        blank=False,
        unique=True,
        null=False
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Ingredients."""

    name = models.CharField(
        verbose_name='Ingredient Name',
        max_length=254
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement Unit',
        max_length=254
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(fields=['name',
                                                       'measurement_unit'],
                                               name='name_measurement_unit')]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Dish Image',
        upload_to='recipes/',
        blank=False,
    )
    name = models.CharField(
        verbose_name='Dish Name',
        max_length=254,
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tag',
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Recipe Text',
        max_length=1000,
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name='Cooking Time',
        validators=[
            MinValueValidator(1, message='Value should be at least 1!'),
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ingredients',
        related_name='recipes',
        through='IngredientInRecipe',
    )
    date = models.DateTimeField(
        verbose_name='Publication Date',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-date',)

    def __str__(self):
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    """Ingredients in Recipe model."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    amount = models.IntegerField(
        verbose_name='Ingriedient Amount',
        default=1
    )

    class Meta:
        verbose_name = 'Ingredient in Recipe'
        verbose_name_plural = 'Ingredients in Recipe'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='ingredient_recipe')]

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class Favorite(models.Model):
    """Favorite recipes model."""

    user = models.ForeignKey(
        User,
        verbose_name='Favorited User',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Favorited Recipes',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='favorite_recipe')]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Shopping cart model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Cart Owner',
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipes in Cart',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Item in Shopping Cart'
        verbose_name_plural = 'Items in Shopping Cart'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='cart_recipe')]

    def __str__(self):
        return f'{self.user} {self.recipe}'
