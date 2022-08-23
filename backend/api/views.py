from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS,
                                        AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Subscription, User
from recipes.models import (Favorite, Ingredient, AddAmount, Recipe,
                            ShoppingCart, Tag)
from .mixins import (ListViewSet, ListRetrieveViewSet)
from .pagination import FoodGramPagination

from .serializers import (CustomUserSerializer,
                          AccountSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeListRetrieveSerializer,
                          RecipeManipulationSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = 'id'
    pagination_class = FoodGramPagination
    http_method_names = ['get', 'head', 'post']

    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        url_path='me',
        serializer_class=AccountSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)


class SubscriptionCreateDeleteAPIView(APIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post', 'delete', )

    def post(self, request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Subscription, user=user, author=author)
        if subscription:
            subscription.delete()
            return Response('Вы отписались от автора.',
                            status=status.HTTP_204_NO_CONTENT)
        return Response('Вы не подписаны на пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = FoodGramPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            return RecipeListRetrieveSerializer
        return RecipeManipulationSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def favorite_adding(self, request, recipe):
        data = {'user': request.user.id, 'recipe': recipe}
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete_from_favorit(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user,
                                           recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(
                'Рецепт удален из Избранного.',
                status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'В Избранном такого рецепта нет.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.favorite_adding(request, recipe.id)
        return self.delete_from_favorit(request, recipe.id)

    @action(methods=('GET',),
            detail=False,
            url_path='download_shopping_cart',
            serializer_class=ShoppingCartSerializer,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = AddAmount.objects.filter(
            recipe__cart__user=request.user).values(
                'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(total=Sum('amount'))
        shopping_cart = '\n'.join([
            f'{ingredient["ingredients__name"]} - {ingredient["total"]} '
            f'{ingredient["ingredients__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def add_to_shopping_cart(self, request, recipe):
        data = {'user': request.user.id, 'recipe': recipe}
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete_from_shopping_cart(self, request, recipe):
        cart = ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe)
        if cart.exists():
            cart.delete()
            return Response(
                'Рецепт удален из Списка покупок.',
                status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'В корзине такого рецепта нет.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe.id)
        return self.delete_from_shopping_cart(request, recipe.id)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer