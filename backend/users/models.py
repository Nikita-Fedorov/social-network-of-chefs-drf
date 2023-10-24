from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from backend.settings import (PASSWORD_MAX_LENGTH, EMAIL_MAX_LENGTH,
                              FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH,
                              USERNAME_MAX_LENGTH)


class User(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True,
    )

    password = models.CharField(
        max_length=PASSWORD_MAX_LENGTH,
        blank=False,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_follow',
                fields=['user', 'author']
            ),
        ]

    def __str__(self):
        return '{} подписан на {}'.format(
            self.user, self.author
        )
