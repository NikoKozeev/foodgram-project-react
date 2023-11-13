from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """User model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        verbose_name='Username',
        max_length=254,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=254,
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=254,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254,
    )
    password = models.CharField(
        verbose_name='Password',
        max_length=254,
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    """Subscription model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='author'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Follower',
        related_name='follower'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'follower'),
                name='author_follower'
            )
        ]

    def __str__(self):
        return f"{self.author} {self.follower}"
