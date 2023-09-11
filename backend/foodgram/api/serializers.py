
import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Cart, Favorite, Ingredient, IngridientForRecipe,
                            Recipe, Tag)
from users.serializers import CustomUserSerializer, RecipeAddSerializer


class Base64ImageField(serializers.ImageField):
    """Поле для кодирования цветов в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализация тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngridientInRecipe(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте"""

    class Meta:
        model = IngridientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        source='ingredient'
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        read_only=True,
        source='ingredient'
    )


class RecipeSerilizers(serializers.ModelSerializer):
    """Сериализатор для чтения(просмотра)рецептов."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngridientInRecipe(many=True, source='ingredient_for_recipe')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_in_shopping_cart(self, obj):
        """Находится ли рецепт в списке покупок."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Cart.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        """Находится ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_authenticated or self.context.get('request'):
            return Favorite.objects.filter(
                user=user, recipe=obj).exists()
        return False


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для создания корзины"""

    class Meta:
        model = Cart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Преобразовать в JSON."""
        return RecipeAddSerializer(instance.recipe, context={
            'request': self.context.get('request')}).data


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания или обновления рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = TagSerializer
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def create_ingredients_amounts(self, ingredients, recipe):
        """Создание для ингредиентов"""
        IngridientForRecipe.objects.bulk_create(
            [IngridientForRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразовать в JSON."""
        return RecipeSerilizers(instance, context={
            'request': self.context.get('request')
        }).data
