from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.serializers import UserSerializer

from .fields import Base64ImageField
from .models import (Ingredients, Recipe, Tag, User,
                     AddIngredientInRec, FavoriteRecipe)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredients
        fields = ('id', 'amount')


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AddIngredientInRec
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = ('amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(source='amounts', many=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'text', 'image',
            'ingredients', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.is_favorited.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.is_in_shopping_cart.filter(user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'text', 'image',
            'ingredients', 'tags', 'cooking_time',
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients_set = set()
        for ingredient in ingredients_data:
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'ИIngredient must be unique'
                )
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Amount must be more then null'
                )
            ingredients_set.add(ingredient['id'])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            id = ingredient['id']
            AddIngredientInRec.objects.create(
                ingredient=get_object_or_404(Ingredients, id=id),
                recipe=recipe, amount=amount
            )
        for tag in tags_data:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_set = set()
        for ingredient in ingredients_data:
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Ingredient must be unique'
                )
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Amount must be more then null'
                )
            ingredients_set.add(ingredient['id'])
        AddIngredientInRec.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            id = ingredient['id']
            AddIngredientInRec.objects.create(
                ingredient=get_object_or_404(Ingredients, id=id),
                recipe=instance, amount=amount
            )
        for tag in tags_data:
            instance.tags.add(tag)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe'
        )

    def validate(self, obj):
        user = self.context['request'].user
        recipe = obj['recipe']
        if (
            self.context.get('request').method == 'POST'
            and user.is_favorited.filter(recipe=recipe).exists()
        ):
            raise serializers.ValidationError(
                'Already in favorite')
        if (
            self.context.get('request').method == 'DELETE'
            and not user.is_favorited.filter(recipe=recipe).exists()
        ):
            raise serializers.ValidationError(
                'You have not that in your favorite')
        return obj


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe'
        )

    def validate(self, obj):
        user = self.context['request'].user
        recipe = obj['recipe']
        if (
            self.context.get('request').method == 'POST'
            and user.is_in_shopping_cart.filter(recipe=recipe).exists()
        ):
            raise serializers.ValidationError(
                'Already in shopping card')
        if (
            self.context.get('request').method == 'DELETE'
            and not user.is_in_shopping_cart.filter(recipe=recipe).exists()
        ):
            raise serializers.ValidationError(
                'That recipe is not in your shopping card')
        return obj
