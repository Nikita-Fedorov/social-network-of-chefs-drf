from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.db.models.expressions import Exists, OuterRef, Value

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from recipe.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart, RecipeIngredient
from api.serializers import (IngredientSerializer, TagSerializers,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             FavoriteSerializer, ShoppingCartSerializer)
from api.permissions import IsAuthorOrReadOnly


class IngridientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializers
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = [IsAuthorOrReadOnly]

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
                is_favorited=Exists(Favorite.objects.filter(user=self.request.user, recipe=OuterRef('pk'))),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(user=self.request.user, recipes=OuterRef('pk')))
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
            return Response({"detail": "Рецепт уже в избранном."},
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
        obj_exists = ShoppingCart.objects.filter(
            user=request.user, recipes=recipe
            ).exists()

        if request.method == 'POST':
            if obj_exists:
                return Response(
                    {'message': 'Рецепт уже находится в списке покупок'},
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

            ShoppingCart.objects.get(user=request.user, recipes=recipe).delete()
            return Response(
                {'message': 'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
                )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipes_in_shopping_cart = [item.recipes for item in shopping_cart]

        # Получаем информацию о продуктах в рецептах
        ingredients_info = RecipeIngredient.objects.filter(recipe__in=recipes_in_shopping_cart)
        ingredients_info = ingredients_info.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            measur_units=F('ingredient__measurement_unit'),
            total=Sum('amount')
        ).order_by('-name')

        # Формируем текстовую строку
        text = 'Список покупок:\n\n' + '\n'.join([
            f"{food['name']} нужно {food['total']} {food['measur_units']}"
            for food in ingredients_info
        ])

        # Создаем HTTP-ответ
        response = Response(text, content_type='application/txt')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'

        return response
