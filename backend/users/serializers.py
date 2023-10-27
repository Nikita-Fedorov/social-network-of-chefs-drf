from rest_framework import serializers

from users.models import Follow, User
from recipe.models import Recipe


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if self.context['request'].method == 'POST':
            author = data.get('author')
            user = self.context['request'].user

            if user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя!'
                )

            if Follow.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора!'
                )

            return data

    def to_representation(self, instance):
        return super().to_representation(instance)


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return SubscribeRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, author=obj).exists()


class UserMeSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields
        read_only_fields = ('is_subscribed',)
