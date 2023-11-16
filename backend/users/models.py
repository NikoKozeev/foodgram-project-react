from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from constants import MAX_LENGTH_NAME, MAX_LENGTH_EMAIL


class User(AbstractUser):
    """User model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        verbose_name='Username',
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=MAX_LENGTH_NAME,
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=MAX_LENGTH_NAME,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Subscription model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='authors'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Subscriber',
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=('authors', 'followers'),
                name='authors_followers'
            )
        ]

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError('You cant subscribe to yourself!')
        return super().clean()

    def __str__(self):
        return f"{self.author} {self.subscriber}"
