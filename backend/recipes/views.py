from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Value, Case, When, Exists, F, Subquery, OuterRef, Q
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .models import Ingredient, Tag, Follow, Recipe, Favorite
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

    '''@action(
        detail=False,
        methods=['GET',],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = SpecialUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)'''

    '''def get_serializer_class(self):
        if self.action == 'create':
            return SpecialUserCreateSerializer
        if self.action == 'me':
            return SpecialUserSerializer
        return SpecialUserSerializer'''


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeRSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeRSerializer
        return RecipeCUDSerializer

