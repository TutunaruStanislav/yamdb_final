import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import User
from reviews.models import Category, Comment, Genre, Review, Title


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'You don`t have to using "me" for username')
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Please use valid username.')
        return value

    class Meta:
        model = User
        fields = ('username',
                  'email', 'first_name', 'last_name', 'bio', 'role',)


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField(allow_null=True)
    code = serializers.CharField(required=False, allow_null=True)

    def validate_confirmation_code(self, value):
        code = self.initial_data.get('code')
        if value and code and value != code:
            raise serializers.ValidationError('Invalid confirmation code')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True, required=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'category', 'genre', 'description', 'rating',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    title = TitleSerializer(required=False)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        author = request.user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        title = get_object_or_404(Title, id=title_id)
        if (
            Review.objects.filter(author=author, title=title).exists()
            and request.method == 'POST'
        ):
            raise serializers.ValidationError(
                'У вас уже есть отзыв на это произведение.'
            )
        return super().validate(data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует!')
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким username уже существует!'
            )
        ]
    )

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                "Нельзя создать пользователя с указанным именем."
            )
        return data


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class SimpleUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        )
        read_only_fields = ('role',)
