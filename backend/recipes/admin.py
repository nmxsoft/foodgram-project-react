from django.contrib import admin

from .models import (Favorite, Ingredient, AddAmount, Recipe,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '---пусто---'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)
    search_fields = ('name', 'slug',)
    list_editable = ('name',)
    empty_value_display = '---пусто---'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name',)
    empty_value_display = '---пусто---'


@admin.register(AddAmount)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredients', 'amount',)
    list_editable = ('ingredients', 'amount',)
    list_filter = ('ingredients',)
    search_fields = ('ingredient_for_recipe__name',)
    empty_value_display = '---пусто---'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    list_editable = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    empty_value_display = '---пусто---'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    list_editable = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    empty_value_display = '---пусто---'
