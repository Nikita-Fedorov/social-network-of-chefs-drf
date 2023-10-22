from django.db import models
from colorfield.fields import ColorField
from sorl.thumbnail import ImageField
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    color = ColorField(default='#FF0000', unique=True, blank=False)
    slug = models.SlugField(unique=True, blank=False)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    image = ImageField(
        upload_to='recipes/images/',
        blank=False,
        default=None
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текст'
    )
    cooking_time = models.IntegerField()
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        through='RecipeTag'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   null=True
                                   )
    amount = models.IntegerField(default=1)


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite_recipe',
                fields=['user', 'recipe']
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart'
                             )
    recipes = models.ForeignKey(Recipe,
                                on_delete=models.CASCADE,
                                related_name='added_to_shopping_cart'
                                )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_in_shoppingcart',
                fields=['user', 'recipes']
            ),
        ]
