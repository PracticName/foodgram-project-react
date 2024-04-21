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
    is_subscribed = serializers.BooleanField(read_only=True)

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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    # is_favorited = serializers.BooleanField(read_only=True)
    # is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
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

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.recipes_userrecipebasemodel_related.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.recipes_userrecipebasemodel_related.filter(recipe=obj).exists()
        return False


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


class RecipeFavSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerialiser(SpecialUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email', 'username', 'first_name', 'last_name',
        )

    def get_recipes_count(self, obj):
        return obj.recipes_author.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')  # GET
        recipes = obj.recipes_author.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeFavSerializer(recipes, many=True, read_only=True)
        return serializer.data
