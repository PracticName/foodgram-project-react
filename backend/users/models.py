from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class MyUser(AbstractUser):
    """Пользователь."""

    email = models.EmailField(
        max_length=settings.LETTERS_IN_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=settings.LETTERS_IN_USERS_FIELD,
        unique=True,
        db_index=True,
        verbose_name='Уникальный юзернейм',
        validators=[ASCIIUsernameValidator(), ]
    )
    first_name = models.CharField(
        max_length=settings.LETTERS_IN_USERS_FIELD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.LETTERS_IN_USERS_FIELD,
        verbose_name='Фамилия'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:settings.FIELDS_SHORT_NAME]
