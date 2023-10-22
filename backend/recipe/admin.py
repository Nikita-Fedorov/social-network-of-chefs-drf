from django.contrib import admin
from .models import Recipe, Ingredient, Tag, RecipeIngredient, RecipeTag


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    pass


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    pass


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAmdin(BaseAdmin):
    inlines = [IngredientInline, TagInline,]
    list_display = (
        'id',
        'author',
        'name',
    )
    list_filter = (
        'author',
    )
    search_fields = ('name',)
