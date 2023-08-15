from rest_framework import serializers

from api.models import Follow, Recipe, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'username', 'password', 'email',
                  'first_name', 'last_name', 'is_subscribed')
        model = User
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.subscriber.filter(user=user).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.subscriber.filter(user=user).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = int(request.query_params.get('recipes_limit', 5))
        recipes = obj.recipes.all()[:limit]
        serializer = SubRecipeSerializer(
            recipes,
            many=True,
            context={'request': request},
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, obj):
        user = obj['user']
        author = obj['author']
        subscribed = user.subscribed_on.filter(author=author).exists()

        if (
            self.context.get('request').method == 'POST'
            and (author == user or subscribed)
        ):
            raise serializers.ValidationError(
                'You can not subscribe again or subs yourself'
            )

        if (
            self.context.get('request').method == 'DELETE'
            and not subscribed
        ):
            raise serializers.ValidationError(
                'This subscribe is absent'
            )
        return obj
