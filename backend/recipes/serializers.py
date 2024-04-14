from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Tag, Follow

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
