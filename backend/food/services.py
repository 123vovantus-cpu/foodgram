from django.utils import timezone
from food.models import RecipeIngredient
from django.db.models import Sum


def generate_shopping_list_text(user):
    ingredients = (
        RecipeIngredient.objects
        .filter(recipe__shoppingcartitems__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(total_amount=Sum("amount"))
        .order_by("ingredient__name")
    )

    lines = [
        "Список покупок",
        f"Дата: {timezone.now().date().strftime('%d.%m.%Y')}",
        f"Пользователь: {user.username}",
        "",
    ]

    for item in ingredients:
        lines.append(
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) — "
            f"{item['total_amount']}"
        )

    return "\n".join(lines)
