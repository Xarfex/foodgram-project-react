import json

from django.core.management.base import BaseCommand
from pathlib import Path

from api.models import Ingredients

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class Command(BaseCommand):
    help = 'Add new ingredients model from ingredients.json'

    def handle(self, *args, **options):
        with open(BASE_DIR / 'data/ingredients.json') as file:
            data = json.load(file)
            for row in data:
                Ingredients.objects.create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],
                )
