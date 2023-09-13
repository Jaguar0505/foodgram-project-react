from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text="Необходимо ввести название тега",
    )

    color = ColorField(
        max_length=7,
        default='#000000',
        unique=True,
        verbose_name='Цвет тега',
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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )]
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(1, message="Введите значение > 0."),
            MaxValueValidator(5999, message="Введите значение < 5999.")
        ]
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name}'


class IngridientForRecipe(models.Model):
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
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(1, message="Введите значение > 0."),
            MaxValueValidator(5999, message="Введите значение < 5999.")
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class AbstractUsersRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def str__(self):
        return f'{self.user}{self.recipe}'


class Favorite(AbstractUsersRecipe):
    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'favorite'
        verbose_name = 'Избранное'


class Cart(AbstractUsersRecipe):
    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'cart'
        verbose_name = 'Корзина'
