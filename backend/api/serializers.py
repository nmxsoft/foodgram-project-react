from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers, status, validators
from djoser.serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',)
        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email',),
                message=(
                    'Комбинация логин-email не совпадают.'
                )
            )
        ]


class SignUpSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='email уже зарегистрирован в системе. Попробуйте снова',
        )]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='Такой логин уже занят. Попробуйте снова.',
        )]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class AccountSerializer(CustomUserSerializer):
    role = serializers.CharField(read_only=True)
