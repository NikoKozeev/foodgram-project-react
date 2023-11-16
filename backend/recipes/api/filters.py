from django_filters import rest_framework
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Filter class for recipes."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(method='favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def shopping_cart_filter(self, queryset, name, value):
        """Filter for recipes in the shopping cart."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart_set__user=self.request.user)
        return queryset

    def favorited_filter(self, queryset, name, value):
        """Filter for favorited recipes."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Filter for changing search to name."""

    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
