from datetime import datetime

from django.db.models import Sum, OuterRef, Subquery
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filter import IngredientFilter, RecipeFilter
from recipes.models import (Cart, Favorite, Ingredient, IngridientForRecipe,
                            Recipe, Tag)

from .serializers import (CartSerializer, CreateRecipeSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerilizers, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.annotate(
        favorited=Subquery(
            Favorite.objects.filter(
                user=OuterRef('author'),
                recipe=OuterRef('pk')
            ).values('pk')[:1]
        ),
        in_shopping_cart=Subquery(
            Cart.objects.filter(
                user=OuterRef('author'),
                recipe=OuterRef('pk')
            ).values('pk')[:1]
        )
    )
    serializer_class = RecipeSerilizers
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerilizers
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteSerializer(recipe,
                                        data=request.data,
                                        context={'request': request}, )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'message': 'Из избранного удален'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = CartSerializer(recipe,
                                    data=request.data,
                                    context={'request': request}, )
        serializer.is_valid(raise_exception=True)
        Cart.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shoping_cart_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'message': 'Из рецепта удален'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status.HTTP_400_BAD_REQUEST)

        ingredients = IngridientForRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(cart_amount=Sum('amount'))
        shopping_list = self.generate_shopping_list(user, ingredients)

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    @staticmethod
    def generate_shopping_list(user, ingredients):
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

        return shopping_list
