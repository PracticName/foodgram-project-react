from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Exists, F, OuterRef, Subquery, Sum, Value
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .pagination import LimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    FollowSerialiser,
    IngredientSerialiser,
    RecipeCUDSerializer,
    RecipeFavSerializer,
    RecipeRSerializer,
    SpecialUserSerializer,
    TagSerializer,
)

import io
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
#    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    http_method_names = ['get', 'head', 'options']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
#    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
#    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    http_method_names = ['get', 'head', 'options']
#    filter_backends = (DjangoFilterBackend,)
#    filterset_class = IngredientFilter

    def get_queryset(self):
        if self.request.query_params.get('name'):
            return Ingredient.objects.filter(
                name__startswith=self.request.query_params.get('name')
            )
        return Ingredient.objects.all()


class SpecialUserViewSet(UserViewSet):
    # permission_classes = (IsAuthenticated,)
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
        return User.objects.annotate(
                is_subscribed=Value(False)
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated,]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
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
            subscription = get_object_or_404(
                Follow,
                user=user,
                following=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated,],
        pagination_class=[LimitPagination,]
    )
    def subscriptions(self, request):
        user = request.user
        # author_recipes = user.recipes_author.all()
        queryset = self.get_queryset().filter(followers__user=user).annotate(
            recipes_count=Count('recipes_author'),
            #  recipes=Subquery(
            #    author_recipes.values('id', 'name', 'image', 'cooking_time')
            # ),
        )
        '''limit = request.query_params.get('recipes_limit')
        if limit:
            queryset = queryset[:int(limit)]
        serializer = FollowSerialiser(queryset, many=True, context={'request': request})
        return Response(serializer.data)'''
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerialiser(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get',],
        permission_classes=[IsAuthenticated,]
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
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeRSerializer
        return RecipeCUDSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_model(Favorite, request.user, pk)
        else:
            return self.delete_model(Favorite, request.user, pk)

    def create_model(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                'Данный рецепт уже в Избранном.',
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serialiser = RecipeFavSerializer(recipe)
        return Response(
            serialiser.data,
            status=status.HTTP_201_CREATED
        )

    def delete_model(self, model, user, pk):
        favorite = model.objects.filter(user=user, recipe__id=pk)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта не существует',
            status=status.HTTP_404_NOT_FOUND
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_model(ShoppingCart, request.user, pk)
        else:
            return self.delete_model(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
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
                dict_key = (f'{ingredient.name}')
                if dict_key in lines:
                    lines[dict_key] += amount
                else:
                    lines[dict_key] = amount
        '''ingredients = RecipeIngredient.objects.filter(
            recipes__author=self.request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(amount=F('amount'))
        lines = {}
        for ingredient in ingredients:
            amount = ingredient['amount']
            dict_key = (f'{ingredient["ingredients__name"]}')
            if dict_key in lines:
                lines[dict_key] += amount
            else:
                lines[dict_key] = amount'''
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
