"""
This script is used to fill the database with data from a csv file.

Place the file in the 'data' folder in the root of the project.
To run it, use the following command:
python manage.py runscript database_script
"""

import csv
import os

from recipes.models import Ingredient, Tag


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_LOCATION = os.path.join(BASE_DIR, 'data', 'ingredients.csv')
TAGS_DATA = [
    {'name': 'Завтрак', 'slug': 'breakfast', 'color': '#ff6600'},
    {'name': 'Обед', 'slug': 'lunch', 'color': '#ff0000'},
    {'name': 'Ужин', 'slug': 'dinner', 'color': '#ff66b2'},
]


def load_ingredients_from_csv(file_path):
    with open(file_path, encoding='utf8') as csv_file:
        ingredients = csv.reader(csv_file)
        Ingredient.objects.all().delete()

        for name, measurement_unit in ingredients:
            Ingredient.objects.get_or_create(name=name,
                                             measurement_unit=measurement_unit)


def fill_tags():
    for tag_data in TAGS_DATA:
        Tag.objects.get_or_create(slug=tag_data['slug'], defaults=tag_data)


def run():
    print('>> Start loading ingredients from csv file')
    load_ingredients_from_csv(DATA_LOCATION)
    print('>> Ingredients loaded successfully')
    print('>> Start filling tags')
    fill_tags()
    print('>> Tags filled successfully')
    print('>> Database filled successfully')
