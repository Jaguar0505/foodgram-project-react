from django.contrib import admin

from recipes.models import Ingredient, IngridientForRecipe, Recipe, Tag


class IngridientForRecipe(admin.TabularInline):
    model = IngridientForRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngridientForRecipe,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
