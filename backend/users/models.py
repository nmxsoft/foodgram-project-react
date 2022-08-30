from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint


class UserRoles:
    USER = 'user'
    ADMIN = 'admin'
    USER_ROLES = (
        (USER, USER),
        (ADMIN, ADMIN),
    )


class User(AbstractUser):

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта',
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]')],
        verbose_name='Ник пользователя',
    )
    role = models.CharField(
        max_length=5,
        choices=UserRoles.USER_ROLES,
        default=UserRoles.USER,
        verbose_name='Права доступа',
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'
        constraints = [
            UniqueConstraint(fields=['email', ], name='email'),
            UniqueConstraint(fields=['username', ], name='username')
        ]

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.role == UserRoles.USER


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='подписка',
        on_delete=models.CASCADE,
        related_name='following',
        error_messages={
            'unique': 'Вы уже подписаны на данного автора.',
        }
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        db_table = 'subscription'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscription'),
            models.CheckConstraint(
                name='do_not_subscribe_again',
                check=~models.Q(user=models.F('author')),
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} оформил подписку на {self.author}'
