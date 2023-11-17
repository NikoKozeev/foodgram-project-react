"""Module for Django models used in the recipes app."""
from django.core.validators import (MinValueValidator,
                                    RegexValidator,
                                    MaxValueValidator)
from django.db import models

from users.models import User
from constants import (MAX_TAG_NAME,
                       MAX_LENGTH_COLOR,
                       MINIMUM_INGREDIENTS,
                       MAX_COOKING_TIME,
                       MAX_AMOUNT,
                       MIN_AMOUNT)


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(
        verbose_name='Name',
        max_length=MAX_TAG_NAME,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Color',
        max_length=MAX_LENGTH_COLOR,
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
        max_length=MAX_TAG_NAME,
        unique=True,
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
        max_length=MAX_TAG_NAME
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement Unit',
        max_length=MAX_TAG_NAME
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
    )
    name = models.CharField(
        verbose_name='Dish Name',
        max_length=MAX_TAG_NAME,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tag',
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Recipe Text',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking Time',
        validators=[
            MinValueValidator(
                MINIMUM_INGREDIENTS,
                message=f'Value should be at least {MINIMUM_INGREDIENTS}!'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Value should be less then {MAX_COOKING_TIME}!'
            ),
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
        return self.name


class IngredientInRecipe(models.Model):
    """Ingredients in Recipe model."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Ingriedient Amount',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Value should be at least {MIN_AMOUNT}!'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                message=f'Value should be less then {MAX_AMOUNT}!'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Ingredient in Recipe'
        verbose_name_plural = 'Ingredients in Recipe'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='ingredient_recipe')]

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class AbstractUserXRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(AbstractUserXRecipe):
    """Favorite recipes model."""

    class Meta:
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='favorite_recipe')]


class ShoppingCart(AbstractUserXRecipe):
    """Shopping cart model."""

    class Meta:
        verbose_name = 'Item in Shopping Cart'
        verbose_name_plural = 'Items in Shopping Cart'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='cart_recipe')]
