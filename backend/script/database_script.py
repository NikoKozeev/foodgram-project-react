import csv
import os

from recipes.models import Ingredient, Tag, User

TAGS_DATA = [
    {'name': 'Breakfast', 'slug': 'breakfast', 'color': '#00ff00'},
    {'name': 'Lunch', 'slug': 'lunch', 'color': '#FF00FF'},
    {'name': 'Dinner', 'slug': 'dinner', 'color': '#0000ff'},
]


def load_ingredients_from_csv(file_path):
    with open(file_path, encoding='utf8') as csv_file:
        ingredients = csv.reader(csv_file)
        for row in ingredients:
            name, measurement_unit = row
            Ingredient.objects.create(name=name,
                                      measurement_unit=measurement_unit)


def create_tags():
    Tag.objects.bulk_create([Tag(**tag_data) for tag_data in TAGS_DATA])


def run():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'ingredients.csv')

    load_ingredients_from_csv(csv_file_path)
    create_tags()
    superuser = User.objects.create_superuser(username='superuser',
                                              email='superuser@mail.ru',
                                              first_name='superuser',
                                              last_name='superuser',
                                              password='superuser')
    superuser.save()
