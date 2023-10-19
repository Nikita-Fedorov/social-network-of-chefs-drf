import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipe.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingCart
from users.serializers import UserSerializer
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id',
                  'name',
                  'measurement_unit')
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        )
    amount = serializers.IntegerField(default=1)

    class Meta:
        fields = 'id', 'amount'
        model = RecipeIngredient


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount'
                  )
        model = RecipeIngredient


class TagSerializers(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    ingridient = IngredientSerializer

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientCreateSerializer(read_only=True, many=True,
                                             source='recipeingredient_set'
                                             )
    tags = TagSerializers(many=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField(read_only=True,
                                                     default=False
                                                     )
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False
                                                   )

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context['request']
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipe=obj
        ).exists():
            return True
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        # Создаем новый рецепт, используя оставшиеся данные
        recipe = Recipe.objects.create(**validated_data)

        # Создаем связи между рецептом и ингредиентами
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.bulk_create(
                [RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data.get('id'),
                    amount=ingredient_data.get('amount'))]
            )

        # Добавляем теги к рецепту
        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        # Обновление ингредиентов
        ingredients_data = validated_data.get('ingredients')
        if ingredients_data:
            instance.ingredients.clear()  # Удалить все существующие ингредиенты
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')
                ingredient = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=amount
                )

        # Обновление тегов
        tags_data = validated_data.get('tags')
        if tags_data:
            instance.tags.set(tags_data)

        instance.save()
        return instance

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

    #     # Обновление ингредиентов
    #     ingredients_data = validated_data.get('ingredients')
    #     if ingredients_data:
    #         updated_ingredients = []  # Для отслеживания обновленных ингредиентов
    #         for ingredient_data in ingredients_data:
    #             ingredient = ingredient_data.get('ingredient')
    #             amount = ingredient_data.get('amount')
    #             existing_ingredient, created = RecipeIngredient.objects.get_or_create(
    #                 recipe=instance,
    #                 ingredient=ingredient,
    #                 defaults={'amount': amount}
    #             )
    #             if not created:
    #                 # Если ингредиент существует, обновляем его количество
    #                 existing_ingredient.amount = amount
    #                 existing_ingredient.save()
    #             updated_ingredients.append(existing_ingredient)

    #         # Удаляем устаревшие ингредиенты, которые не были обновлены
    #         instance.ingredients.exclude(id__in=[ingredient.id for ingredient in updated_ingredients]).delete()

    #     # Обновление тегов
    #     tags_data = validated_data.get('tags')
    #     if tags_data:
    #         instance.tags.set(tags_data)

    #     instance.save()
    #     return instance

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

    #     # Обновление ингредиентов
    #     ingredients_data = validated_data.get('ingredients')
    #     if ingredients_data:
    #         for ingredient_data in ingredients_data:
    #             ingredient, created = RecipeIngredient.objects.get_or_create(
    #                 recipe=instance,
    #                 ingredient=ingredient_data.get('ingredient'),
    #                 defaults={'amount': ingredient_data.get('amount')}
    #             )

    #     # Обновление тегов
    #     tags_data = validated_data.get('tags')
    #     if tags_data:
    #         instance.tags.set(tags_data)

    #     instance.save()
    #     return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={
                'request': self.context.get('request')
            }
        ).data

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')
        model = Recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite

    def to_representation(self, instance):
        return FavoriteRecipeSerializer(
            instance.recipe,
            context={'request': self.context['request']}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
