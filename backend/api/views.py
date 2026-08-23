from django.shortcuts import render
import os
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from food.models import (Favorite, Follow, Ingredient, Recipe,
                         RecipeIngredient, ShoppingCartItem, Tag)

from api.serializers import (FollowedUserSerializer, FoodgramUserSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, ShortRecipeSerializer,
                             TagSerializer)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django_filters.filterset import FilterSet
from django_filters.filters import CharFilter
from rest_framework.decorators import action
from django.http import FileResponse 
from rest_framework.response import Response
from django.utils.timezone import now
from django.db import models
from django.template.loader import render_to_string 
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.urls import reverse
from django_filters import rest_framework as filters
from food.models import Recipe, Tag
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from django_filters.rest_framework.backends import DjangoFilterBackend

User = get_user_model()

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']

class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        label='tags',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, recipes, name, value):
        user = self.request.user
        if value and not user.is_anonymous:

            return recipes.filter(favorites__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return recipes.filter(shoppingcartitems__user=user)
        return recipes


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = IngredientFilter

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart and user.is_authenticated:
            cart_subquery = ShoppingCartItem.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            queryset = queryset.annotate(
                in_cart=Exists(cart_subquery)
            ).filter(in_cart=True)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError(f"Рецепт с id={pk} не найден.")
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipe-short-link', args=[pk])
            )},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[AllowAny]
    )
    def set_image(self, request):
        recipe = request.recipe
        image = request.data.get('image')

        if not image:
            return Response(
                {'image': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем текущий путь старого аватара (если есть)
        old_image_path = recipe.image.path if recipe.image else None

        # Создаем новый файл аватара, не удаляя пока старый
        recipe.image = (
            RecipeReadSerializer().fields['image'].to_internal_value(image))
        recipe.save()

        # Удаляем старый файл, если он был и отличается от нового
        if old_image_path and os.path.isfile(old_image_path):
            try:
                # Проверяем, что новый файл не совпадает с удаляемым
                if old_image_path != recipe.image.path:
                    os.remove(old_image_path)
            except Exception:
                # На всякий случай подавляем ошибку удаления,
                # чтобы не ломать ответ
                pass

        return Response(
            {'image': recipe.image.url if recipe.image else None},
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(
            shoppingcartitems__user=user)

        content = render_to_string('shopping_list.txt', {
            'user': user,
            'date': now().date(),
            'ingredients': (
                RecipeIngredient.objects.filter(
                    recipe__in=recipes
                ).values(
                    'ingredient__name', 'ingredient__measurement_unit'
                ).annotate(
                    total_amount=models.Sum('amount')
                ).order_by('ingredient__name')
            ),
            'recipes': recipes,
        })

        return FileResponse(
            content, as_attachment=True, filename='shopping_list.txt')

    def handle_add_or_remove(self, model, recipe_id, request):
        if request.method not in {'POST', 'DELETE'}:
            return Response(
                {'error': f'Метод {request.method} не поддерживается'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        if request.method == 'DELETE':
            get_object_or_404(
                model,
                user=request.user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # if request.method == 'POST':
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        obj, created = model.objects.get_or_create(user=request.user,
                                                   recipe=recipe)
        if not created:
            raise ValidationError(
                f'Рецепт с id={recipe.id} '
                f'уже добавлен в {model._meta.verbose_name_plural.lower()}.')

        return Response(
            ShortRecipeSerializer(
                recipe,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.handle_add_or_remove(
            model=ShoppingCartItem,
            request=request,
            recipe_id=pk
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.handle_add_or_remove(
            model=Favorite,
            recipe_id=pk,
            request=request,
        )