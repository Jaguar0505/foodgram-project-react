# Generated by Django 2.2.19 on 2023-08-08 08:55

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Список покупок',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Укажите единицу измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngridientForRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Введите значение > 0.')], verbose_name='Количество ингредиента')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_for_recipe', to='recipes.Ingredient', verbose_name='Ингридиент')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Количество ингридиентов',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Необходимо ввести название тега', max_length=200, verbose_name='Название тега')),
                ('color', models.CharField(help_text='Введите цвет формата #HEX', max_length=7, unique=True, validators=[django.core.validators.RegexValidator('^\\#[\\dA-F]{6}$')], verbose_name='Цвет тега')),
                ('slug', models.SlugField(help_text='Введите слаг', max_length=200, unique=True, verbose_name='Слаг тега')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='Картинка, закодированная в Base64')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Введите значение > 0.')], verbose_name='Время приготовления (в минутах)')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.IngridientForRecipe', to='recipes.Ingredient', verbose_name='Список ингредиентов')),
                ('tags', models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Список id тегов')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AddField(
            model_name='ingridientforrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_for_recipe', to='recipes.Recipe', verbose_name='Рецепт'),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.Recipe', verbose_name='Избранное')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
            },
        ),
    ]