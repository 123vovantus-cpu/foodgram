from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserWithSubscriptionViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

api = DefaultRouter()

api.register("ingredients", IngredientViewSet, basename="ingredients")
api.register("recipes", RecipeViewSet, basename="recipes")
api.register("tags", TagViewSet, basename="tags")
api.register("users", UserWithSubscriptionViewSet, basename="users")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(api.urls)),
]
