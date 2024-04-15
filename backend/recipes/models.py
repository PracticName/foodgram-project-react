from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from colorfield.fields import ColorField

User = get_user_model()


class NameBaseModel(models.Model):
    """Абстрактная модель с полем name."""
    name = models.CharField(
        'Название',
        max_length=settings.LETTERS_IN_FIELD
    )

    class Meta:
        abstract = True
        ordering = ('-name',)

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


class Ingredient(NameBaseModel):
    """Ингредиенты для рецепта."""
    measurement_unit = models.CharField(
        'Единицы измерения.',
        max_length=settings.LETTERS_IN_FIELD
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Follow(UserBaseModel):
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE, related_name='followers'
    )


class Recipe(NameBaseModel):
    """Рецепты пользователя."""
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                limit_value=settings.MIN_VALUE_SCORE,
                message=('Время приготовления должно быть '
                         f'меньше {settings.MIN_VALUE_SCORE} минуты')
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


class RecipeIngredient(models.Model):
    """Ингредиенты для конкретного рецепта с количеством."""
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
        validators=[
            MinValueValidator(
                limit_value=settings.MIN_VALUE_SCORE,
                message=('Количество не должно быть '
                         f'меньше {settings.MIN_VALUE_SCORE} ед.')
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

    class Meta(UserBaseModel.Meta):
        pass


class Favorite(UserRecipeBaseModel):
    """Избранные рецепты пользователя."""
    pass


class ShoppingCart(UserRecipeBaseModel):
    """Подписка на рецепты пользователя."""
    pass
