from django.core.exceptions import ValidationError
import django_filters

from recipes.models import Ingredient, Recipe
from users.models import User


class TagsMultipleChoiceField(
        django_filters.fields.MultipleChoiceField):

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'], code='required')
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice', params={'value': val},)


class TagsFilter(django_filters.AllValuesMultipleFilter):
    field_class = TagsMultipleChoiceField


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = django_filters.BooleanFilter(
        widget=django_filters.widgets.BooleanWidget(), label='В корзине.')
    is_favorited = django_filters.BooleanFilter(
        widget=django_filters.widgets.BooleanWidget(), label='В избранных.')
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug', label='Ссылка')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
