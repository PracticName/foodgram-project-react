# praktikum_new_diplom
Создайте пустую миграцию 
python manage.py makemigrations --empty appname

Создается примерно такая миграция:
import csv

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
    ]

Далеее добавьте в operations операцию RunPython. Она запускает функцию, которую вы ей предадите.

 operations = [
        migrations.RunPython(copy_ingredients),
    ]
Осталось только написать эту функцию:

import csv

from django.conf import settings
from django.db import migrations


def copy_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    with open(
        str(settings.CUR_DIR) + '/data/' + 'ingredients.csv',
        'r',
        encoding='utf-8'
    ) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1]
            )


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240412_1759'),
    ]

    operations = [
        migrations.RunPython(copy_ingredients),
    ]
