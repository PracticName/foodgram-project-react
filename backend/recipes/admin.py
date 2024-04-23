from django.contrib import admin

from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


admin.site.empty_value_display = 'Не задано'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс настройки подписок на пользователя."""

    list_display = (
        'id',
        'user',
        'following',
    )
    list_editable = ('user', 'following')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки Тегов."""

    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_editable = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки Ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки Рецепта."""

    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
    )
    list_editable = ('name', 'text', 'cooking_time')
    list_filter = ('author',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """ласс настройки Рецепта с Ингридеентом."""

    list_display = (
        'recipes',
        'ingredients',
        'amount',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс настройки Рецепта."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_editable = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс настройки Рецепта."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_editable = ('user', 'recipe')
    list_filter = ('user', 'recipe')
