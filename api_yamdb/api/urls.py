from django.urls import include, path
from rest_framework import routers

from . import views
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
urlpatterns = [
    path('v1/auth/signup/', views.auth_signup, name='auth_signup'),
    path('v1/auth/token/', views.auth_token, name='auth_token'),
    path('v1/users/me/', views.users_me, name='users_me'),
    path('v1/', include(router.urls)),
]
