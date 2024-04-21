from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.db import models

from .validators import validate_username


'''class MyUserManager(BaseUserManager):
    """Класс менеджера пользователей."""

    def create_user(
            self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('Введите адрес электронной почты.')
        if not username:
            raise ValueError('Введите свой юзернейм.')
        if not password:
            raise ValueError('Введите пароль.')
        if not first_name:
            raise ValueError('Введите Ваше Имя.')
        if not last_name:
            raise ValueError('Введите Вашу Фамилию.')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email, username, first_name, last_name, password=None):
        user = self.create_user(
            email, username, first_name, last_name, password
        )
        user.is_superuser = True
        user.save(self._db)
        return user'''


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
        validators=[ASCIIUsernameValidator(),]
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
