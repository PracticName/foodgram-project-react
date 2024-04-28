from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class NameBaseModel(models.Model):
    """Абстрактная модель с полем name."""
    name = models.CharField(
        'Название',
        max_length=settings.LETTERS_IN_FIELD
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.FIELDS_SHORT_NAME]


class UserBaseModel(models.Model):
    """Абстрактная модель с полем user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related'
    )

    class Meta:
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return self.user.username[:settings.FIELDS_SHORT_NAME]


class Tag(NameBaseModel):
    """Тег рецепта."""
    color = ColorField(
        'Цвет в HEX'
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=settings.LETTERS_IN_FIELD,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Поле содержите недопустимый символ'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.FIELDS_SHORT_NAME]


class Ingredient(NameBaseModel):
    """Ингредиенты для рецепта."""
    measurement_unit = models.CharField(
        'Единицы измерения.',
        max_length=settings.LETTERS_IN_FIELD
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name[:settings.FIELDS_SHORT_NAME]}, '
                f'{self.measurement_unit}')


class Follow(UserBaseModel):
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        verbose_name = 'Подписка на рецепт'
        verbose_name_plural = 'Подписка на рецепты'
        ordering = ('id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'Подписка {self.user.username} на {self.following.username}'


class Recipe(NameBaseModel):
    """Рецепты пользователя."""
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                limit_value=settings.MIN_VALUE_SCORE,
                message=('Время приготовления должно быть '
                         f'больше {settings.MIN_VALUE_SCORE} минуты.')
            ),
            MaxValueValidator(
                limit_value=settings.MAX_VALUE_SCORE,
                message=('Время приготовления должно быть '
                         f'меньше {settings.MAX_VALUE_SCORE} минут.')
            )
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_author'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags_recipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов',
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name[:settings.FIELDS_SHORT_NAME]


class RecipeIngredient(models.Model):
    """Ингредиенты для конкретного рецепта с количеством."""
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
        validators=[
            MinValueValidator(
                limit_value=settings.MIN_VALUE_SCORE,
                message=('Количество не должно быть '
                         f'меньше {settings.MIN_VALUE_SCORE} ед.')
            ),
            MaxValueValidator(
                limit_value=settings.MAX_VALUE_SCORE,
                message=('Количество не должно быть '
                         f'больше {settings.MAX_VALUE_SCORE} ед.')
            )
        ]
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='reciepes'
    )

    class Meta:
        verbose_name = 'Ингридеент Рецепта'
        verbose_name_plural = 'Ингридеенты Рецепта'
        ordering = ('-id',)

    def __str__(self):
        return (f'{self.ingredients.name[:settings.FIELDS_SHORT_NAME]}, '
                f'{self.ingredients.measurement_unit} - '
                f'{self.amount}'
                )


class UserRecipeBaseModel(UserBaseModel):
    """Абстрактная модель с полем recipe.
       Расширяет абстрактную модель UserBaseModel.
       Используется в классах Favorite и ShoppingCart.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related'
    )

    class Meta:
        abstract = True
        ordering = ('-recipe',)

    def __str__(self):
        return self.recipe.name[:settings.FIELDS_SHORT_NAME]


class Favorite(UserRecipeBaseModel):
    """Избранные рецепты пользователя."""
    pass

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-recipe',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return (f'{self.user.username[:settings.FIELDS_SHORT_NAME]} '
                f'- {self.recipe.name[:settings.FIELDS_SHORT_NAME]}')


class ShoppingCart(UserRecipeBaseModel):
    """Добавление рецепта в корзину."""
    pass

    class Meta:
        verbose_name = 'Корзина рецепта'
        verbose_name_plural = 'Корзина рецептов'
        ordering = ('-recipe',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return (f'{self.user.username[:settings.FIELDS_SHORT_NAME]} '
                f'- {self.recipe.name[:settings.FIELDS_SHORT_NAME]}')
