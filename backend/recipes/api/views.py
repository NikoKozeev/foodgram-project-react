"""This module contains views for recipe-related actions."""
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.api.filters import IngredientFilter, RecipeFilter
from recipes.api.serializers import (IngredientSerializer,
                                     RecipePostSerializer, RecipeSerializer,
                                     TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.api.pagination import UserPagination
from users.api.permissions import AuthorOrReadOnly
from users.api.serializers import FavoriteSerializer, ShoppingCartSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """View for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    paginator = None


class RecipesViewSet(ModelViewSet):
    """View for recipes."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = UserPagination

    def get_serializer_class(self):
        """Select a serializer."""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Create a recipe."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Update a created recipe."""
        serializer.save(author=self.request.user)

    @staticmethod
    def shopping_cart_and_favorite_serialization(serializer, request, pk):
        """Add or remove a recipe from the shopping cart or favorites."""
        context = {'request': request}
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True,
            )
    def shopping_cart(self, request, pk):
        """Add/Remove a recipe from the shopping cart."""
        if request.method == 'POST':
            return self.shopping_cart_and_favorite_serialization(
                ShoppingCartSerializer, request, pk)
        else:
            data = ShoppingCart.objects.filter(
                user_id=request.user.id, recipe_id=pk
            )
            if data.exists():
                data.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            get_object_or_404(Recipe, id=pk)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def favorite(self, request, pk):
        """Add/Remove favorite recipes."""
        if request.method == 'POST':
            return self.shopping_cart_and_favorite_serialization(
                FavoriteSerializer, request, pk)

        data = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        get_object_or_404(Recipe, id=pk)
        return Response({'Error': 'No such recipe'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False)
    def download_shopping_cart(self, request):
        """Download the shopping cart."""
        if request.user.shopping_cart.exists():
            ingredients_recipe = IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user)
            values = ingredients_recipe.values('ingredient__name',
                                               'ingredient__measurement_unit')
            ingredients = values.annotate(amount=Sum('amount'))

            shopping_cart = 'Shopping Cart.\n'
            list_order = 0
            for ingredient in ingredients:
                list_order += 1
                shopping_cart += (
                    f'{list_order}) '
                    f'{ingredient["ingredient__name"][0].upper()}'
                    f'{ingredient["ingredient__name"][1:]} - '
                    f'{ingredient["ingredient__measurement_unit"]} '
                    f'({ingredient["amount"]})\n'
                )

            filename = 'ShoppingCart.txt'
            response = HttpResponse(shopping_cart,
                                    content_type='text/plain')
            response['Content-Disposition'] = (f'attachment; '
                                               f'filename={filename}')
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """View for ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)
    filterset_class = IngredientFilter
