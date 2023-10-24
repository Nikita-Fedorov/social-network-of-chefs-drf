from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField
from sorl.thumbnail import ImageField

from users.models import User
from backend.settings import (MAX_COOKING_TIME, MIN_COOKING_TIME,
                              MEASHUREMENT_UNIT_MAX_LENGTH, TAG_MAX_LENGTH,
                              NAME_MAX_LENGTH)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASHUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Название'
    )
    color = ColorField(
        default='#FF0000',
        unique=True,
        blank=False,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    image = ImageField(
        upload_to='recipes/images/',
        blank=False,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текст'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(limit_value=MIN_COOKING_TIME),
            MaxValueValidator(limit_value=MAX_COOKING_TIME)
        ],
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        through='RecipeTag',
        verbose_name='Тэг'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(limit_value=MIN_COOKING_TIME),
            MaxValueValidator(limit_value=MAX_COOKING_TIME)
        ],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return 'Ингредиент {} добавлен в рецепт {}.'.format(
            self.ingredient.name, self.recipe.name
        )


class RecipeTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('recipe',)

    def __str__(self):
        return 'Тег {} выбран к рецепту {}.'.format(
            self.tag.name, self.recipe.name
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite_recipe',
                fields=['user', 'recipe']
            )
        ]

    def str(self):
        return 'Рецепт {} добавлен в избранное.'.format(self.recipe.name)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='added_to_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_in_shoppingcart',
                fields=['user', 'recipes']
            ),
        ]

    def str(self):
        return 'Рецепт {} добавлен в список покупок'.format(self.recipes.name)
