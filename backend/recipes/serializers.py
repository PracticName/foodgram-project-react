import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.db import transaction
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.generics import get_object_or_404
from rest_framework import serializers

from recipes.models import Ingredient, Tag, Follow, RecipeIngredient, Recipe

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега (модель Tag) рецепа."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для ингредиентов (модель RecipeIngredient) рецепта."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class SpecialUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SpecialUserSerializer(UserSerializer):
    """Сериализатор текущего пользователя."""
    # is_subscribed = serializers.BooleanField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Follow.objects.filter(
                user=current_user, following=obj).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeRSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = SpecialUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
        #    'is_favorited',
        #    'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('tags', 'author')

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredients__amount')
        )
        return ingredients


class RecipeCUDSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = SpecialUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
        #    'is_favorited',
        #    'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    @transaction.atomic
    def create_recipeingredient(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                recipes=recipe,
                amount=ingredient['amount']
                ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipeingredient(ingredients=ingredients, recipe=recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeRSerializer(instance, context=context).data
