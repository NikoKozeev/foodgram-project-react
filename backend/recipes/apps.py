"""Class for Recipe configuration."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Class responsible for the configuration of the recipes app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
