from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from food.models import (Favorite, Follow, Ingredient, Recipe,
                         RecipeIngredient, ShoppingCartItem, Tag)
import base64
import uuid
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.db import models    

User = get_user_model()



RECIPE_MIN_COOKING_TIME = 1  
INGREDIENT_MIN_AMOUNT = 1  

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):

            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)

class FoodgramUserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (*DjoserUserSerializer.Meta.fields, 'avatar', 'is_subscribed')
        read_only_fields = fields

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request
            and not request.user.is_anonymous
            and Follow.objects.filter(author=author,
                                      follower=request.user).exists()
        )



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name='Продукт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Мера',
        help_text='Мера продукта в рецепте'
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]