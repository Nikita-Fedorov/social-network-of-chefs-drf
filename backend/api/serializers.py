import base64
from django.core.files.base import ContentFile
from rest_framework import serializers


from recipe.models import (Ingredient, Recipe,
                           RecipeIngredient, Tag,
                           Favorite)
from users.serializers import UserSerializer
from backend.settings import MAX_COOKING_TIME, MIN_COOKING_TIME


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
    amount = serializers.IntegerField(max_value=MAX_COOKING_TIME,
                                      min_value=MIN_COOKING_TIME
                                      )

    class Meta:
        fields = ('id',
                  'amount')
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

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientCreateSerializer(read_only=True, many=True,
                                             source='recipeingredient_set'
                                             )
    tags = TagSerializers(many=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.BooleanField(read_only=True,
                                            default=False
                                            )
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False
                                                   )
    cooking_time = serializers.IntegerField(max_value=MAX_COOKING_TIME,
                                            min_value=MIN_COOKING_TIME
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


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    def validate_recipe(self, data):
        if self.context['request'].method == 'POST':
            name = data.get('name')
            author = self.context['request'].user
            if author.recipes.filter(name=name).exists():
                raise serializers.ValidationError(
                    'Вы уже создали рецепт с таким названием!',
                )
            return data

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                'Рецепт нельзя создать без ингредиентов!'
            )
        names = []
        for ingredient in data:
            ingredient_name = ingredient.get('ingredient', {}
                                             ).get('id', {}
                                                   ).get('name')
            if ingredient_name:
                names.append(ingredient_name)

        if len(names) != len(set(names)):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться!'
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Рецепту нужен хотя бы один тег!'
            )
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными!'
            )

        return data

    def create_or_update_ingredients(self, instance, ingredients_data):

        new_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]

        RecipeIngredient.objects.bulk_create(new_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        self.create_or_update_ingredients(recipe, ingredients_data)

        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        instance.save()

        self.create_or_update_ingredients(instance, ingredients_data)

        instance.tags.set(tags)

        return instance

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
