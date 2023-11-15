import csv
import os

from recipes.models import Ingredient, Tag


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_LOCATION = os.path.join(BASE_DIR, 'ingredients.csv')
TAGS_DATA = [
    {'name': 'First Course', 'slug': 'first', 'color': '#ff6600'},
    {'name': 'Main Course', 'slug': 'main', 'color': '#ff0000'},
    {'name': 'Desert', 'slug': 'desert', 'color': '#ff66b2'},
]


def import_ingredients_from_csv_file(file_path):
    with open(file_path, encoding='utf8') as data_file:
        ingredients = csv.reader(data_file)
        for row in ingredients:
            name, measurement_unit = row
            Ingredient.objects.create(name=name,
                                      measurement_unit=measurement_unit)


def fill_tags():
    """Создает тэги и сохраняет их в базе данных."""
    Tag.objects.bulk_create([Tag(**tag_data) for tag_data in TAGS_DATA])


def run():
    import_ingredients_from_csv_file(DATA_LOCATION)
    fill_tags()
