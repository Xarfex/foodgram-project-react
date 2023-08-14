from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User's model"""
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'login',
        max_length=100,
        unique=True,
        null=True
    )
    password = models.CharField(
        'password',
        max_length=100,
        null=True
    )
    first_name = models.CharField(
        'first name',
        max_length=100,
        blank=True
    )
    last_name = models.CharField(
        'last name',
        max_length=100,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return f'{self.username}'
