# Generated by Django 3.2.16 on 2023-09-09 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_author'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingridientforrecipe',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Количество ингредиентов'},
        ),
    ]