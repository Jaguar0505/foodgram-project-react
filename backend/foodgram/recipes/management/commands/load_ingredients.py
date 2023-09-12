import csv
import logging

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(filename='import.log', level=logging.INFO)
        self.import_ingredients()
        logging.info('База загружена.')

    def import_ingredients(self, file='ingredients.csv'):
        logging.info(f'Данные загружены из {file}')
        path = f'./data/{file}'
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
