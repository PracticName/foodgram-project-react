import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега рецепа."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientRSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента с полем amount рецепта.
       На чтение.
    """
    ingredients = IngredientSerialiser(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('ingredients', 'amount')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ingredients = ret.pop('ingredients')
        for key in ingredients:
            ret[key] = ingredients[key]
        return ret


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента с полем amount рецепта.
       На запись.
    """
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        min_value=settings.MIN_VALUE_SCORE,
        max_value=settings.MAX_VALUE_SCORE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class SpecialUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


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
    """Сериализатор рецепта только на чтение."""
    tags = TagSerializer(many=True)
    author = SpecialUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientRSerializer(many=True, source='reciepes')

    image = Base64ImageField()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

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


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериализатор создания, редактирования и удаления рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = SpecialUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=settings.MIN_VALUE_SCORE,
        max_value=settings.MAX_VALUE_SCORE
    )

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
        read_only_fields = ('author',)

    def validate(self, attrs):
        if 'tags' not in attrs:
            raise serializers.ValidationError(
                'Отсутствует поле tags',
                status.HTTP_400_BAD_REQUEST
            )
        if 'ingredients' not in attrs:
            raise serializers.ValidationError(
                'Отсутствует поле ingredients',
                status.HTTP_400_BAD_REQUEST
            )
        return super().validate(attrs)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Пустое поле ingredients',
                status.HTTP_400_BAD_REQUEST
            )
        ingredients = []
        for ingredient in value:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    detail='Ингридент не существует',
                    code=status.HTTP_400_BAD_REQUEST
                )
            obj = Ingredient.objects.get(id=ingredient['id'])
            if obj in ingredients:
                raise serializers.ValidationError(
                    detail=f'Ингридент {obj} можно добавить только один раз',
                    code=status.HTTP_400_BAD_REQUEST
                )
            ingredients.append(obj)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                detail='Пустое поле tags',
                code=status.HTTP_400_BAD_REQUEST
            )
        tags = []
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    detail=f'Тег {tag} можно добавить только один раз',
                    code=status.HTTP_400_BAD_REQUEST
                )
            tags.append(tag)
        return value

    @transaction.atomic
    def create_recipeingredient(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                recipes=recipe,
                amount=ingredient['amount']) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipeingredient(ingredients=ingredients, recipe=recipe)
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        recipe.author.is_subscribed = False
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_recipeingredient(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeRSerializer(instance, context=context).data


class RecipeFavSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для подписки и покупок."""
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
    """Сериализатор подписок."""
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

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
            'email', 'username', 'first_name', 'last_name', 'is_subscribed',
        )

    def get_recipes(self, obj):
        '''request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')'''
        limit = self.context.get('recipes_limit')
        recipes = obj.recipes_author.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeFavSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def validate(self, attrs):
        following = self.instance
        user = self.context.get('id')
        if following == user:
            raise ValidationError(
                'Нельзя подписаться на себя!',
                status.HTTP_400_BAD_REQUEST
            )
        if user.recipes_follow_related.all():
            raise ValidationError(
                'Нельзя подписаться на одного пользователя дважды!',
                status.HTTP_400_BAD_REQUEST
            )
        return attrs
