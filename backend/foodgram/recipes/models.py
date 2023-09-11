from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text="Необходимо ввести название тега",
    )
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(r'^\#[\dA-F]{6}$')],
        unique=True,
        verbose_name='Цвет тега',
        help_text="Введите цвет формата #HEX"
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=200,
        help_text="Введите слаг",
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингридиента"""
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text="Укажите единицу измерения"
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептa."""
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Список ингредиентов',
        through='IngridientForRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список id тегов'
    )
    image = models.ImageField('Картинка, закодированная в Base64')
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    text = models.TextField('Описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1, message="Введите значение > 0.")]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name}'


class IngridientForRecipe(models.Model):
    """Модель ингредиента в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Ингридиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1, message="Введите значение > 0.")]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'


class Cart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Покупатель',
                             related_name='cart'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Корзина',
                               related_name='cart')

    class Meta:
        verbose_name = 'Список покупок'


class Favorite(models.Model):
    """Модель списка избранного."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Выбиратель',
                             related_name='favorite'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Избранное',
                               related_name='favorite'
                               )

    class Meta:
        verbose_name = 'Избранный рецепт'
