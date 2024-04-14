from django.contrib import admin

from .models import Follow, Recipe, Ingredient, Tag, RecipeIngredient, Favorite, ShoppingCart


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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки подписок на пользователя."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
