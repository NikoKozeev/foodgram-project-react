from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Admin for the Tag model."""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('id', 'name', 'color', 'slug')
    list_filter = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin for the Ingredient model."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin for the Favorite model."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user',)


@admin.register(IngredientInRecipe)
class IngredientsOfRecipeAdmin(admin.ModelAdmin):
    """Admin for the IngredientInRecipe model."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient', 'amount')
    list_filter = ('ingredient',)


class RecipeIngredientAdmin(admin.StackedInline):
    """Ingriedients in admin Recipe."""

    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)
    min_num = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Admin for the Recipe model."""

    list_display = ('id', 'author',
                    'name', 'text', 'cooking_time',
                    'favorite_count', 'image',
                    'recipes_tags', 'recipes_ingredients')
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name', 'cooking_time', 'tags__name',
                     'author__email', 'ingredients__name')
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='tags')
    def recipes_tags(self, obj):
        """Return the tags of the recipe."""
        return ', '.join((tag.name for tag in obj.tags.all()))

    @admin.display(description='ingredients')
    def recipes_ingredients(self, obj):
        """Return the ingredients of the recipe."""
        return ', '.join((
            ingredient.name[0].upper() + ingredient.name[1:]
            for ingredient in obj.ingredients.all()
        ))

    @admin.display(description='favorite count')
    def favorite_count(self, obj):
        """Return number of times the recipe has been marked as favorite."""
        return obj.favorite_set.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin for the ShoppingCart model."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
