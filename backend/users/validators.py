import re

from django.core.exceptions import ValidationError


def validate_username(username):
    pattern = re.compile(r'^[\w.@+-]+\z')

    if pattern.fullmatch(username) is None:
        match = re.split(pattern, username)
        symbol = ''.join(match)
        raise ValidationError(f'Некорректные символы в username: {symbol}')
    return username
