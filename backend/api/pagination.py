from rest_framework.pagination import PageNumberPagination
from food.constants import (
    RECIPE_PAGINATION_PAGE_SIZE,
    RECIPE_PAGINATION_MAX_PAGE_SIZE,
    RECIPE_PAGINATION_LIMIT_PARAM,
)


class RecipePagination(PageNumberPagination):
    page_size = RECIPE_PAGINATION_PAGE_SIZE
    max_page_size = RECIPE_PAGINATION_MAX_PAGE_SIZE
    page_size_query_param = RECIPE_PAGINATION_LIMIT_PARAM
