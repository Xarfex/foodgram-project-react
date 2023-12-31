from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientsViewSet, RecipeViewSet
from users.views import UserViewSet

app_name = 'api'


router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
]
