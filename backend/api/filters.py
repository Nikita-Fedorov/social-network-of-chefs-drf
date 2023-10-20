from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter, ChoiceFilter
from recipe.models import Ingredient, Recipe, Tag
from users.models import User

BOOL_CHOICES = (
    ('0', 'False'),
    ('1', 'True'),
)


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all(), label='Автор')
    is_favorited = ChoiceFilter(label='Избранное', choices=BOOL_CHOICES, method='get_filter_favorite')
    is_in_shopping_cart = ChoiceFilter(label='Корзина', choices=BOOL_CHOICES, method='get_filter_shopping_cart')
    tags = ModelMultipleChoiceFilter(label='Тэги', queryset=Tag.objects.all(), field_name='tags__slug', to_field_name='slug')

    class Meta:
        model = Recipe
        fields = 'author', 'tags'

    def get_filter_favorite(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(favorite__user=user) if user.is_authenticated and value else queryset

    def get_filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(added_to_shopping_cart__user=user) if user.is_authenticated and value else queryset
