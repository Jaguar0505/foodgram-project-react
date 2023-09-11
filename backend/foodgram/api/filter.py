from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_favorited = filters.BooleanFilter(
        method='favorite',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='cart',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def favorite(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError(
                "Авторизируйся, что бы иметь право фильтровать избранное."
            )
        return queryset.filter(favorite__user=user)

    def cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError(
                "Авторизируйся, что бы иметь право фильтровать покупки."
            )
        return queryset.filter(cart__user=user)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
