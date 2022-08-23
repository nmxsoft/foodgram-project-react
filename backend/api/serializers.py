from rest_framework import exceptions, serializers, status, validators
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import Subscription, User
from recipes.models import (Favorite, Ingredient, AddAmount, Recipe,
                            ShoppingCart, Tag)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',)
        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',
                            'is_subscribed',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email',),
                message=(
                    'Комбинация логин-email не совпадают.'
                )
            )
        ]

    def get_is_subscribed(self, obj: User):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )


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

    def validate_username(self, username: str):
        """Validation of user's username"""
        if username.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя')
        return username

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


class PartialRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',)

    def get_recipes(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return PartialRecipeSerializer(
            recipes, many=True, context=context).data

    def get_recipes_count(self, obj: User):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Recipe.objects.filter(author=obj).count()
        else:
            raise exceptions.NotAuthenticated(
                detail='Учетные данные не были предоставлены.',
                code=status.HTTP_401_UNAUTHORIZED
            )


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message=('Подписка уже есть')
            )
        ]

    def validate(self, data):
        user = self.context.get('request').user
        subscription_id = data.get('id')
        user_id = data.get('user_id')
        author_id = data.get('author_id')
        subscription = Subscription.objects.filter(id=subscription_id,
                                                   user=user_id,
                                                   author=author_id).exists()
        if subscription:
            raise serializers.ValidationError(
                detail=(f'Вы уже подписаны на {author_id}.'),
                code=status.HTTP_400_BAD_REQUEST
            )
        if author_id == user.id:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionListSerializer(
            instance.author, context=context).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AddAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = AddAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class AddAmountCUDSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = AddAmount
        fields = ('id', 'amount',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients',
        read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def get_ingredients(self, obj: Recipe):
        ingredients = AddAmount.objects.filter(recipe=obj)
        return AddAmountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj: Recipe):
        if self.context.get('request').method == 'POST':
            return False
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.user_favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        if self.context.get('request').method == 'POST':
            return False
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.user_cart.filter(recipe=obj).exists()
        return False


class RecipeManipulationSerializer(serializers.ModelSerializer):
    ingredients = AddAmountCUDSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',)

    def create_ingredients(self, recipe, ingredients):
        bulk_list = []
        for ingredient in ingredients:
            bulk_list.append(AddAmount(
                recipe=recipe,
                ingredients=ingredient.get('id'),
                amount=ingredient.get('amount'),
            ))
        return AddAmount.objects.bulk_create(bulk_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        instance.tags.set(tags)
        AddAmount.objects.filter(recipe=recipe).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(recipe, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListRetrieveSerializer(
            instance,
            context={'request': self.context.get('request')}).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=('Рецепт уже в избранном')
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return PartialRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message=('Рецепт уже есть в списке покупок')
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return PartialRecipeSerializer(
            instance.recipe, context=context).data
