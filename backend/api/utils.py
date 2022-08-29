from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import AddAmount


def download_txt_ingredients(request):
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
