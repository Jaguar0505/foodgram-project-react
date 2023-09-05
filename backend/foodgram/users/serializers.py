import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Recipe

from .models import Subscribe

User = get_user_model()

logger = logging.getLogger(__name__)


class RegisterUserSerializer(serializers.ModelSerializer):
    """Сериализатор формы регистрации пользователя"""
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="Минимум 8 символов.",
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  "password", 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserSerilizer(serializers.ModelSerializer):
    """Пользовательский сериализатор"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user,
                                        author=obj).exists()


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
