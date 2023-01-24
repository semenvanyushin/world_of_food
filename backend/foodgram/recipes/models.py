from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'название тега', max_length=30, blank=False, null=False,
    )
    color = models.CharField(
        'цвет тега', max_length=10, blank=False, null=False,
    )
    slug = models.SlugField(
        'слаг тега', unique=True, db_index=True, blank=False, null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название ингридиента', max_length=150, blank=False, null=False,
    )
    measurement_unit = models.CharField(
        'единица измерения', max_length=50, blank=False, null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe', verbose_name='автор'
    )
    name = models.CharField(
        'название рецепта', max_length=200, blank=False, null=False,
    )
    image = models.ImageField(
        'изображение', upload_to='static/recipes/',
        blank=False, null=False,
    )
    text = models.TextField(
        'текстовое описание', blank=False, null=False,
    )
    ingredient = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
    )
    tag = models.ManyToManyField(
        Tag, through='RecipeTag', related_name='recipes',
    )
    cooking_time = models.IntegerField(
        'время приготовления', blank=False, null=False,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipes'
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tags')

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient'
    )
    quantity = models.IntegerField()

    class Meta:
        ordering = ['-id']
        verbose_name = 'количество ингридиента'
        verbose_name_plural = 'количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
