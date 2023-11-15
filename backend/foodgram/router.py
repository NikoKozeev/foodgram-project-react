"""Module for defining API routes."""
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from recipes.api.views import IngredientsViewSet, RecipesViewSet, TagsViewSet
from users.api.views import CustomUserViewSet

app_name = 'api'
router = SimpleRouter()


router.register('users',
                CustomUserViewSet, basename='users')
router.register('tags',
                TagsViewSet, basename='tags')
router.register('recipes',
                RecipesViewSet, basename='recipes')
router.register('ingredients',
                IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
