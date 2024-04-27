import io

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Value
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import LimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerialiser, IngredientSerialiser,
                          RecipeCUDSerializer, RecipeFavSerializer,
                          RecipeRSerializer, SpecialUserSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get', 'head', 'options']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerialiser
    pagination_class = None
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        if self.request.query_params.get('name'):
            return Ingredient.objects.filter(
                name__startswith=self.request.query_params.get('name')
            )
        return Ingredient.objects.all()


class SpecialUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPagination

    def get_queryset(self):
        if self.get_instance().is_authenticated:
            queryset = User.objects.annotate(
                is_subscribed=Exists(
                    Follow.objects.filter(
                        user=self.get_instance(),
                        following=OuterRef('id')
                    )
                ),
                recipes_count=Count('recipes_author'),
            )
            return queryset
        return User.objects.annotate(is_subscribed=Value(False))

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(self.get_queryset(), id=author_id)
        if request.method == 'POST':
            serializer = FollowSerialiser(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, following=author).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription = Follow.objects.get(
                user=user,
                following=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
    )
    def subscriptions(self, request):
        user = request.user
        queryset = self.get_queryset().filter(followers__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerialiser(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get', ],
    )
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        me_user = get_object_or_404(queryset, pk=request.user.id)
        serializer = SpecialUserSerializer(me_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Recipe.objects.annotate(
                is_favorited=Exists(
                    user.recipes_favorite_related.filter(
                        recipe=OuterRef('id'))
                ),
                is_in_shopping_cart=Exists(
                    user.recipes_shoppingcart_related.filter(
                        recipe=OuterRef('id'))
                )
            )
            return queryset

        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        )

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrive':
            return (AllowAny(),)
        if (self.action == 'destroy'
                or self.action == 'update'
                or self.action == 'partial_update'):
            return (IsAuthorOrReadOnly(),)
        return (IsAuthenticatedOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeRSerializer
        return RecipeCUDSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_model(Favorite, request.user, pk)
        return self.delete_model(Favorite, request.user, pk)

    def create_model(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                'Рецепт не существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                'Данный рецепт уже добавлен.',
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = self.get_object()
        model.objects.create(user=user, recipe=recipe)
        serialiser = RecipeFavSerializer(recipe)
        return Response(
            serialiser.data,
            status=status.HTTP_201_CREATED
        )

    def delete_model(self, model, user, pk):
        recipe = self.get_object()
        if not model.objects.filter(user=user, recipe=recipe):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite_or_cart = model.objects.filter(user=user, recipe__id=pk)
        if favorite_or_cart.exists():
            favorite_or_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта не существует',
            status=status.HTTP_404_NOT_FOUND
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_model(ShoppingCart, request.user, pk)
        return self.delete_model(ShoppingCart, request.user, pk)

    @action(
        detail=False,
    )
    @transaction.atomic
    def download_shopping_cart(self, request):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        pdfmetrics.registerFont(TTFont(
            'DejaVuSerif', 'DejaVuSerif.ttf')
        )
        textob.setFont('DejaVuSerif', 14)
        recipes = ShoppingCart.objects.filter(user=self.request.user)
        lines = {}
        for recipe in recipes:
            for ingredient in recipe.recipe.ingredients.all():
                amount = RecipeIngredient.objects.filter(
                    recipes=recipe.recipe,
                    ingredients=ingredient
                ).first().amount
                dict_key = (f'{ingredient.name} -- '
                            f'{ingredient.measurement_unit}')
                if dict_key in lines:
                    lines[dict_key] += amount
                else:
                    lines[dict_key] = amount
        for key, value in lines.items():
            textob.textLine(f'{key}--{value}')
        c.drawText(textob)
        c.showPage
        c.save()
        buf.seek(0)
        return FileResponse(
            buf,
            as_attachment=True,
            filename='cart.pdf',
        )
