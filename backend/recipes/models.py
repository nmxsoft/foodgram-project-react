from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from .validators import validate_not_empty

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        null=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        blank=False
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        default='#123456',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='slug тега',
        blank=False,
        unique=True,
        max_length=200,
        db_index=True,
        error_messages={
            'unique': 'Выбранный slug уже существует.',
        }
    )

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        db_table = 'slug'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'slug',),
                name='unique_slug'),
            models.CheckConstraint(
                name='not_double_slug',
                check=~models.Q(name=models.F('slug')),
            )
        ]

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        validators=[validate_not_empty]
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте рецепт',
        max_length=10000,
        validators=[validate_not_empty]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AddAmount',
        related_name='recipes',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах.',
        null=False,
        validators=[MinValueValidator(
            1, message='Минимальное время приготовления = 1 минута.')]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text

    def get_absoulute_url(self):
        return reverse('recipe', args=[self.pk])


class AddAmount(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Ингредиент',
        null=True,
    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='ingredients_recipes')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента для рецепта',
        null=False,
        validators=[MinValueValidator(
            1, message='Минимальное количество должно быть не меньше 1.')]
    )

    class Meta:
        verbose_name = 'Количество ингредиента для рецепта'
        verbose_name_plural = 'Количество ингредиента для рецептов'

    def __str__(self) -> str:
        return f'{self.ingredients} - {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        db_table = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_favorites'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        db_table = 'cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]
