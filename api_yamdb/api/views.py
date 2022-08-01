import random
from http import HTTPStatus

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import User, Review, Title, Genre, Category

from .filters import TitleFilter
from .pagination import UsersPagination
from .permissions import AdminOnly, IsAdmin, IsAuthor, IsModerator, ReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer,
    ReviewSerializer, TitleSerializer, TitleSerializerGet,
    UserSerializer, AuthSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_signup(request):
    username = request.data.get('username')
    email = request.data.get('email')

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()

    code = str(random.randint(100000, 999999))
    request.session[username] = code

    send_mail(
        'Получение доступа',
        f'username: {username}. '
        f'Для получение токена доступа к api, передайте следующий код '
        f'подтверждения: {code}',
        'yamdb@mail.net',
        [email],
        fail_silently=False,
    )

    return Response(data=request.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_token(request):
    username = request.data.get('username')
    data = {
        'username': username,
        'confirmation_code': request.data.get('confirmation_code'),
        'code': request.session.get(username),
    }

    serializer = AuthSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=username)

    return Response(data={
        'token': str(RefreshToken.for_user(user).access_token)
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def users_me(request):
    instance = User.objects.get(pk=request.user.id)
    serializer = UserSerializer(instance)
    if request.method == 'PATCH':
        if request.data.get('role') and instance.role == 'user':
            request.data._mutable = True
            request.data.pop('role', None)
            request.data._mutable = False

        serializer = UserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = UsersPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (AdminOnly, )

    def get_queryset(self):
        username = self.request.parser_context.get('kwargs').get('pk')
        if username:
            return get_object_or_404(User, username=username)

        return User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_queryset())
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_queryset(),
                                    data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_queryset())
        return Response(status=HTTPStatus.NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReadOnly | IsAuthor | IsModerator | IsAdmin]
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ReadOnly | IsAuthor | IsModerator | IsAdmin]
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly | IsAdmin]
    lookup_field = 'slug'
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [ReadOnly | IsAdmin]
    lookup_field = 'slug'
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [ReadOnly | IsAdmin]
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializerGet
        return TitleSerializer
