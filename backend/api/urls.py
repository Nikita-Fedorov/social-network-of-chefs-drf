from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import IngridientViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()


router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
