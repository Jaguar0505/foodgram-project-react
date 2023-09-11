# Generated by Django 3.2.16 on 2023-09-06 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20230906_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, help_text='Обязательно для заполнения', max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, help_text='Обязательно для заполнения', max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Обязательно для заполнения', max_length=150, unique=True, verbose_name='Уникальный юзернейм'),
        ),
    ]