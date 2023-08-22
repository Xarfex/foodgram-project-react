import json

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from api.models import Ingredients


class Command(BaseCommand):
    help = 'Add new ingredients model from ingredients.json'

    def handle(self, *args, **options):
        with open(BASE_DIR / 'data/ingredients.json') as file:
            data = json.load(file)
            Ingredients.objects.bulk_create(
                Ingredients(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                for row in data
            )
