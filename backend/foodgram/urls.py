from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, TagViewSet, SpecialUserViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
# router.register(r'users', SpecialUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
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
            {'get': 'set_password'}
        ), name='set_password'
    ),
    path('api/auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
