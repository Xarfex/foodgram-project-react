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
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .serializers import (TagSerializer, IngredientReadSerializer,
                          FavoriteRecipeSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)
from .filters import IngredientNameFilter, RecipeFilter
from .models import (Ingredients, Recipe, ShoppingList, Tag,
                     AddIngredientInRec, FavoriteRecipe)
from .pagination import CustomPageSizePagination
from .permissions import AuthPostRetrieve, IsAuthorOrReadOnly
import api.constants as c


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


class RecipeViewSet(ModelViewSet):
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
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            ShoppingList.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        file_name = c.FILE_NAME
        doc_title = c.DOC_TITLE
        title = c.TITLE
        sub_title = f'{timezone.now().date()}'
        response = HttpResponse(content_type='application/pdf')
        content_disposition = f'attachment; filename="{file_name}.pdf"'
        response['Content-Disposition'] = content_disposition
        pdf = canvas.Canvas(response)
        pdf.setTitle(doc_title)
        pdfmetrics.registerFont(TTFont('Dej', 'DejaVuSans.ttf'))
        pdf.setFont('Dej', c.FONT_SIZE_TITLE)
        pdf.drawCentredString(c.X_FOR_TITLE, c.Y_FOR_TITLE, title)
        pdf.setFont('Dej', c.FONT_SIZE_SUB_TITLE)
        pdf.drawCentredString(c.X_FOR_SUB_TITLE, c.Y_FOR_SUB_TITLE, sub_title)
        pdf.line(c.X1, c.Y1, c.X2, c.Y2)
        height = c.Y_FOR_INGREDIENTS
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
