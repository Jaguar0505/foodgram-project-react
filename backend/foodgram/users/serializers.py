from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe

from .models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user,
                                        author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def validate(self, data):
        """Валидация подписки повторной/самого на себя"""
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )

        return data

    def get_recipes_count(self, obj):
        """Получаем кол-во рецептов"""
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        """Получаем рецепты"""
        recipes = obj.recipes.all()
        serializer = RecipeAddSerializer(recipes, many=True, read_only=True)
        return serializer.data


class RecipeAddSerializer(serializers.ModelSerializer):
    "Краткий сериализатор для добавления рецепта"

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
