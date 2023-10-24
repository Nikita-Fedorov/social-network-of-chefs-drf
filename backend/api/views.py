from django.db.models import Exists, F, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.pagination import RecipePagination
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             TagSerializers)


class IngridientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializers
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'tags',
            'ingredients',
            'author'
        )

        if self.request.user.is_authenticated:
            recipes = recipes.annotate(
                is_favorited=Exists(
                    self.request.user.users_favorite.filter(
                        recipe=OuterRef('pk')
                    )),
                is_in_shopping_cart=Exists(
                    self.request.user.shopping_cart.filter(
                        in_shopping_cart__pk=OuterRef('pk')
                        ))
            )

        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[IsAuthenticated]
            )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            recipe=recipe
        )

        if request.method == 'POST':
            if created:
                serializer = FavoriteSerializer(favorite,
                                                context={'request': request}
                                                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            return Response({'message': 'Рецепт уже в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite,
                user=request.user,
                recipe=get_object_or_404(Recipe, pk=pk)
            )
            self.perform_destroy(favorite)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete',),
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj_exists = request.user.shopping_cart.filter(
            in_shopping_cart=recipe
        ).exists()

        if request.method == 'POST':
            if obj_exists:
                return Response(
                    {'message': 'Рецепт уже находится в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=request.user, recipes=recipe)
            return Response(
                {'message': 'Рецепт добавлен в список покупок'},
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if not obj_exists:
                return Response(
                    {'message': 'Рецепт уже удален из списка покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.get(user=request.user,
                                     recipes=recipe).delete()
            return Response(
                {'message': 'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.shopping_cart.all()
        recipes_in_shopping_cart = [item.recipes for item in shopping_cart]

        ingredients_info = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_shopping_cart
        )
        ingredients_info = ingredients_info.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            measur_units=F('ingredient__measurement_unit'),
            total=Sum('amount')
        ).order_by('-name')

        text = 'Список покупок:\n\n' + '\n'.join([
            (f"{food['name']} — {food['total']} {food['measur_units']}")
            for food in ingredients_info
        ])

        response = HttpResponse(text, content_type='application/txt')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping_cart.txt"'
        )
        return response
