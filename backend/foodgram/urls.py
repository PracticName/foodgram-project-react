from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    SpecialUserViewSet,
    TagViewSet,
)

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path(
        'api/users/', SpecialUserViewSet.as_view(
            {'get': 'list', 'post': 'create'}
        ), name='users'
    ),
    path(
        'api/users/<int:id>/', SpecialUserViewSet.as_view(
            {'get': 'retrieve'}
        ), name='user_pk'
    ),
    path(
        'api/users/me/', SpecialUserViewSet.as_view(
            {'get': 'me'}
        ), name='user_me'
    ),
    path(
        'api/users/set_password/', SpecialUserViewSet.as_view(
            {'post': 'set_password'}
        ), name='set_password'
    ),
    path(
        'api/users/<int:id>/subscribe/',
        SpecialUserViewSet.as_view(
            {'post': 'subscribe', 'delete': 'subscribe'}
        ),
        name='subscribe'
    ),
    path(
        'api/users/subscriptions/',
        SpecialUserViewSet.as_view({'get': 'subscriptions'}),
        name='subscriptions'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
