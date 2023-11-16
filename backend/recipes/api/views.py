from io import StringIO
from django.db.models import Sum
from django.http import FileResponse
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
                                     TagSerializer,
                                     FavoriteSerializer, 
                                     ShoppingCartSerializer)
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from users.api.pagination import UserPagination
from users.api.permissions import AuthorOrReadOnly


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """View for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    paginator = None


class RecipesViewSet(ModelViewSet):
    """View for recipes."""

    queryset = Recipe.objects.all().select_related('author').prefetch_related(
        'tags', 'ingredients_in_recipe')
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = UserPagination

    def get_serializer_class(self):
        """Select a serializer."""
        if self.request.method in ('POST', 'PATCH',):
            return RecipePostSerializer
        return RecipeSerializer

    @staticmethod
    def shopping_cart_and_favorite_serialization(serializer, request, pk):
        """Add or remove a recipe from the shopping cart or favorites."""
        context = {'request': request}
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'],
            permission_classes=[IsAuthenticated],
            detail=True,
            )
    def shopping_cart(self, request, pk):
        """Add a recipe from the shopping cart."""
        return self.shopping_cart_and_favorite_serialization(
            ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        """Delete a recipe from the shopping cart."""
        data = ShoppingCart.objects.filter(
            user_id=request.user.id, recipe_id=pk
        )
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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

    @staticmethod
    def get_shopping_cart_txt_response(ingredients):
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
        response_data = StringIO(shopping_cart)
        return FileResponse(
            response_data,
            as_attachment=True,
            filename=filename,
            content_type='text/plain'
        )

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False)
    def download_shopping_cart(self, request):
        """Download the shopping cart."""
        if request.user.shoppingcart_set.exists():
            ingredients = IngredientInRecipe.objects\
                .filter(recipe__shoppingcart_set__user=request.user)\
                .values('ingredient__name', 'ingredient__measurement_unit')\
                .annotate(amount=Sum('amount'))
            return self.get_shopping_cart_txt_response(ingredients)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """View for ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)
    filterset_class = IngredientFilter
