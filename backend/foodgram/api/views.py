from datetime import datetime

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filter import IngredientFilter, RecipeFilter
from recipes.models import (Cart, Favorite, Ingredient, IngridientForRecipe,
                            Recipe, Tag)
from users.serializers import RecipeAddSerializer

from .serializers import (CartSerializer, CreateRecipeSerializer,
                          IngredientSerializer, RecipeSerilizers,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    "Вьюха для рецептов"
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerilizers
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Переопределение на основании выбора действия"""
        if self.action in ['create', 'partial_update', 'update']:
            return CreateRecipeSerializer
        return RecipeSerilizers

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_fav(Favorite, request.user, pk)
        return self.delete_fav(Favorite, request.user, pk)

    def add_fav(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже был добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeAddSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_fav(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже был удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок"""

        data = {'recipe': pk,
                'user': request.user.id}
        if request.method == 'POST':
            serializer = CartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        Cart.objects.filter(**data).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в *txt."""
        user = request.user
        if not user.cart.exists():
            return Response(status.HTTP_400_BAD_REQUEST)

        ingredients = IngridientForRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(cart_amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["cart_amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
