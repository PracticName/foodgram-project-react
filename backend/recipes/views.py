from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Value, Case, When, Exists, F, Subquery, OuterRef, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404

from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Tag, Follow, Recipe, Favorite, ShoppingCart
from .pagination import CurrentPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import IngredientSerialiser, TagSerializer, SpecialUserSerializer, SpecialUserCreateSerializer, RecipeRSerializer, RecipeCUDSerializer, RecipeFavSerializer, FollowSerialiser

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerialiser
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        return Ingredient.objects.filter(
            name__startswith=self.request.query_params.get('name')
        )


class SpecialUserViewSet(UserViewSet):
    pagination_class = CurrentPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.get_instance().is_authenticated:
            queryset = User.objects.annotate(
                is_subscribed=Exists(
                    Follow.objects.filter(
                        user=self.get_instance(),
                        following=OuterRef('id')
                    )
                )
            )
            return queryset
        return User.objects.annotate(
                is_subscribed=Value(False)
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
#        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        print('1111111111111111111111')
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
#        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        print('2222222222222222222222')
        user = request.user
        queryset = User.objects.filter(followers__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerialiser(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['get',],
        permission_classes=[IsAuthenticated,]
    )
    def me(self, request):
        queryset = self.get_queryset()
        me_user = get_object_or_404(queryset, pk=request.user.id)
        serializer = SpecialUserSerializer(me_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeRSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CurrentPagination

    '''def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Recipe.objects.annotate(
                is_favorited=Exists(user.recipes_userrecipebasemodel_related.filter(recipe=OuterRef('id'))))
            return queryset
        # .annotate(is_in_shopping_cart=Value(False))
        return Recipe.objects.annotate(is_favorited=Value(False))'''

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
            status=status.HTTP_400_BAD_REQUEST
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
