from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Value, Case, When
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .models import Ingredient, Tag, Follow, Recipe
from .serializers import IngredientSerialiser, TagSerializer, SpecialUserSerializer, SpecialUserCreateSerializer, RecipeRSerializer, RecipeCUDSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser


class SpecialUserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()

    '''def get_current_obj(self):
        return get_object_or_404(
                User, id=self.kwargs.get('id'),
            )

    def get_queryset(self):
        request_user = self.get_instance()
        queryset = User.objects.all()
        if request_user.is_authenticated:
            if self.action == 'list':
                for current_user in queryset:
                    queryset = User.objects.annotate(
                        is_subscribed=(
                            Value(
                                any(user.id == current_user.id for user in request_user.recipes_follow_related.all())
                            )
                        )
                    )
                return queryset
            if self.action == 'me':
                queryset = User.objects.annotate(
                    is_subscribed=(
                        Value(False)
                    )
                )
                return queryset
            obj_user = self.get_current_obj()
            queryset = User.objects.annotate(
                is_subscribed=(
                    Value(
                        any(user.id == obj_user.id for user in request_user.recipes_follow_related.all())
                    )
                )
            )
            return queryset          
        queryset = User.objects.annotate(
            is_subscribed=(Value(False))
            )
        return queryset'''
    '''def get_user(self):
        return get_object_or_404(
                User, id=self.kwargs.get('id'),
            )'''

    '''def get_queryset(self):
        request_user = self.request.user
        if request_user.is_anonymous:
            queryset = User.objects.annotate(
                is_subscribed=Value(False)
            )
            return queryset
        queryset = User.objects.annotate(
            is_subscribed=Value(
                Follow.objects.filter(
                    user=request_user.id, following=Value('id').exists()
            )
        )
        return queryset'''


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeRSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeRSerializer
        return RecipeCUDSerializer
