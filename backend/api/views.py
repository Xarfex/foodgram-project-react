from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet,
                                     ReadOnlyModelViewSet, mixins)

from .serializers import (TagSerializer, IngredientReadSerializer,
                          FavoriteRecipeSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)
from .filters import IngredientNameFilter, RecipeFilter
from .models import (Ingredients, Recipe, ShoppingList, Tag,
                     AddIngredientInRec, FavoriteRecipe)
from .pagination import CustomPageSizePagination
from .permissions import AuthPostRetrieve, IsAuthorOrReadOnly


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    permission_classes = AllowAny
    serializer_class = IngredientReadSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = IngredientNameFilter


class RecipeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = [AuthPostRetrieve, IsAuthorOrReadOnly]
    pagination_class = CustomPageSizePagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.id,
            'recipe': pk,
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        if (
            request.method == 'POST'
            and serializer.is_valid()
        ):
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        if (
            request.method == 'DELETE'
            and serializer.is_valid()
        ):
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        data = {
            'user': user.id,
            'recipe': pk,
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        if (
            request.method == 'POST'
            and serializer.is_valid()
        ):
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        if (
            request.method == 'DELETE'
            and serializer.is_valid()
        ):
            ShoppingList.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.is_in_shopping_cart.all()
        shopping_list = {}
        for item in shopping_cart:
            recipe = item.recipe
            ingredients = AddIngredientInRec.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    shopping_list[name]['amount'] += amount
        file_name = 'Shopping_list'
        doc_title = 'Recipes in the shopping list'
        title = 'Shopping list'
        sub_title = f'{timezone.now().date()}'
        response = HttpResponse(content_type='application/pdf')
        content_disposition = f'attachment; filename="{file_name}.pdf"'
        response['Content-Disposition'] = content_disposition
        pdf = canvas.Canvas(response)
        pdf.setTitle(doc_title)
        pdfmetrics.registerFont(TTFont('Dej', 'DejaVuSans.ttf'))
        pdf.setFont('Dej', 24)
        pdf.drawCentredString(300, 770, title)
        pdf.setFont('Dej', 16)
        pdf.drawCentredString(290, 720, sub_title)
        pdf.line(30, 710, 565, 710)
        height = 670
        for name, data in shopping_list.items():
            pdf.drawString(
                50,
                height,
                f"{name} - {data['amount']} {data['measurement_unit']}"
            )
            height -= 25
        pdf.showPage()
        pdf.save()
        return response
