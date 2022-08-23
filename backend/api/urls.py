from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet,
                    RecipeViewSet,
                    SubscriptionCreateDeleteAPIView)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users_list')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

app_name = 'api'

urlpatterns = [
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='docs'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscriptionCreateDeleteAPIView.as_view(),
        name='subscribe'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
