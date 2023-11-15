import csv
import os

from recipes.models import Ingredient, Tag


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_LOCATION = os.path.join(BASE_DIR, 'ingredients.csv')
TAGS_DATA = [
    {'name': 'Завтрак', 'slug': 'breakfast', 'color': '#ff6600'},
    {'name': 'Обед', 'slug': 'lunch', 'color': '#ff0000'},
    {'name': 'Ужин', 'slug': 'dinner', 'color': '#ff66b2'},
]


def load_ingredients_from_csv(file_path):
    with open(file_path, encoding='utf8') as csv_file:
        ingredients = csv.reader(csv_file)
        for row in ingredients:
            name, measurement_unit = row
            Ingredient.objects.create(name=name,
                                      measurement_unit=measurement_unit)


def fill_tags():
    Tag.objects.bulk_create([Tag(**tag_data) for tag_data in TAGS_DATA])


def run():
    load_ingredients_from_csv(DATA_LOCATION)
    fill_tags()
