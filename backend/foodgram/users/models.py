from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты',
        help_text='Обязательно для заполнения'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Уникальный юзернейм',
        help_text='Обязательно для заполнения',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=False,
        help_text='Обязательно для заполнения',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=False,
        help_text='Обязательно для заполнения',
    )
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль",
        blank=False,
        help_text="Обязательно для заполнения"
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.username}: {self.first_name}'


class Subscribe(models.Model):
    """Модель для подписчиков."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscrib',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор')

    class Meta:
        ordering = ('-id'),
        verbose_name = "Подписка",
        verbose_name_plural = "Подписки"
