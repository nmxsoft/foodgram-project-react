from django.contrib.auth.password_validation import (
    password_validators_help_texts, validate_password)
from rest_framework import serializers, status


def password_verification(value):
    help_text = password_validators_help_texts()
    if validate_password(value) is None:
        return value
    raise serializers.ValidationError(
        detail=f'Введите новый пароль отвечающий требованиям: {help_text}',
        code=status.HTTP_400_BAD_REQUEST
    )
