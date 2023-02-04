from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('название тега', max_length=50, unique=True)
    color = models.CharField('цвет тега', max_length=10, unique=True)
    slug = models.SlugField('слаг тега', max_length=100, unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('название ингридиента', max_length=150)
    measurement_unit = models.CharField('единица измерения', max_length=50)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe', verbose_name='автор')
    name = models.CharField('название рецепта', max_length=200)
    image = models.ImageField('изображение', upload_to='static/recipes/')
    text = models.TextField('текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='теги')
    cooking_time = models.IntegerField(
        'время приготовления',
        validators=[validators.MinValueValidator(
            1, message='Не меньше 1 минуты'), ])
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient')
    amount = models.FloatField(
        default=1,
        verbose_name='количество',
        validators=[validators.MinValueValidator(
            1, message='Не меньше 1'), ])

    class Meta:
        ordering = ['-id']
        verbose_name = 'количество ингридиента'
        verbose_name_plural = 'количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_ingredient')]


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор')
    created = models.DateTimeField('дата подписки', auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription')]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class FavoriteRecipe(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True,
        related_name='favorite_recipe',
        verbose_name='пользователь')
    recipe = models.ManyToManyField(
        Recipe, related_name='favorite_recipe',
        verbose_name='избранный рецепт')

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'

    def __str__(self):
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f'{self.user} добавил {list_} в избранное.'

    @receiver(post_save, sender=User)
    def create_shopping_cart(sender, instance, created, **kwargs):
        if created:
            return FavoriteRecipe.objects.create(user=instance)


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True,
        related_name='shopping_cart',
        verbose_name='пользователь')
    recipe = models.ManyToManyField(
        Recipe, related_name='shopping_cart',
        verbose_name='покупка')

    class Meta:
        ordering = ['-id']
        verbose_name = 'покупка продукта'
        verbose_name_plural = 'покупка продуктов'

    def __str__(self):
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f'{self.user} добавил {list_} в список покупок.'

    @receiver(post_save, sender=User)
    def create_shopping_cart(sender, instance, created, **kwargs):
        if created:
            return ShoppingCart.objects.create(user=instance)
