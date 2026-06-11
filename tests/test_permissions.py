import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from api.permissions import (AdminOnly, IsAdmin, IsAuthor, IsModerator,
                             ReadOnly)
from reviews.models import User


@pytest.fixture
def factory():
    """DRF request factory.

    :author: claude
    """
    return APIRequestFactory()


@pytest.fixture
def user_admin(db):
    """Create admin user.

    :author: claude
    """
    return User.objects.create_user(
        username='admin_user',
        password='pass',
        role='admin'
    )


@pytest.fixture
def user_moderator(db):
    """Create moderator user.

    :author: claude
    """
    return User.objects.create_user(
        username='moderator_user',
        password='pass',
        role='moderator'
    )


@pytest.fixture
def user_regular(db):
    """Create regular user.

    :author: claude
    """
    return User.objects.create_user(
        username='regular_user',
        password='pass',
        role='user'
    )


@pytest.fixture
def user_superuser(db):
    """Create superuser (is_superuser=True).

    :author: claude
    """
    return User.objects.create_superuser(
        username='superuser',
        email='super@test.com',
        password='pass'
    )


class TestAdminOnly:
    """Test AdminOnly permission class.

    :author: claude
    """

    def test_admin_user_has_permission(self, factory, user_admin):
        """Admin user (role='admin') has permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_admin
        permission = AdminOnly()
        assert permission.has_permission(request, None) is True

    def test_superuser_has_permission(self, factory, user_superuser):
        """Superuser has permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_superuser
        permission = AdminOnly()
        assert permission.has_permission(request, None) is True

    def test_regular_user_denied(self, factory, user_regular):
        """Regular user (role='user') denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = AdminOnly()
        assert permission.has_permission(request, None) is False

    def test_moderator_denied(self, factory, user_moderator):
        """Moderator user denied (not admin).

        :author: claude
        """
        request = factory.get('/')
        request.user = user_moderator
        permission = AdminOnly()
        assert permission.has_permission(request, None) is False

    def test_anonymous_denied(self, factory):
        """Anonymous user denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = AnonymousUser()
        permission = AdminOnly()
        assert permission.has_permission(request, None) is False


class TestReadOnly:
    """Test ReadOnly permission class.

    :author: claude
    """

    def test_get_allowed(self, factory, user_regular):
        """GET request allowed.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is True

    def test_head_allowed(self, factory, user_regular):
        """HEAD request allowed.

        :author: claude
        """
        request = factory.head('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is True

    def test_options_allowed(self, factory, user_regular):
        """OPTIONS request allowed.

        :author: claude
        """
        request = factory.options('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is True

    def test_post_denied(self, factory, user_regular):
        """POST request denied.

        :author: claude
        """
        request = factory.post('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is False

    def test_patch_denied(self, factory, user_regular):
        """PATCH request denied.

        :author: claude
        """
        request = factory.patch('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is False

    def test_delete_denied(self, factory, user_regular):
        """DELETE request denied.

        :author: claude
        """
        request = factory.delete('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_permission(request, None) is False

    def test_object_permission_get_allowed(
        self, factory, user_regular
    ):
        """Object permission: GET allowed.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_object_permission(
            request, None, None
        ) is True

    def test_object_permission_post_denied(
        self, factory, user_regular
    ):
        """Object permission: POST denied.

        :author: claude
        """
        request = factory.post('/')
        request.user = user_regular
        permission = ReadOnly()
        assert permission.has_object_permission(
            request, None, None
        ) is False


class TestIsAuthor:
    """Test IsAuthor permission class.

    :author: claude
    """

    def test_authenticated_has_permission(
        self, factory, user_regular
    ):
        """Authenticated user has has_permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = IsAuthor()
        assert permission.has_permission(request, None) is True

    def test_anonymous_denied_permission(self, factory):
        """Anonymous user denied has_permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = AnonymousUser()
        permission = IsAuthor()
        assert permission.has_permission(request, None) is False

    def test_author_owns_object(
        self, factory, user_regular
    ):
        """Author can access own object (has_object_permission).

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular

        # Mock object with author = current user
        class MockObject:
            author = user_regular

        permission = IsAuthor()
        assert permission.has_object_permission(
            request, None, MockObject()
        ) is True

    def test_non_author_denied_object(
        self, factory, user_regular, user_admin
    ):
        """Non-author denied object access.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular

        # Mock object with different author
        class MockObject:
            author = user_admin

        permission = IsAuthor()
        assert permission.has_object_permission(
            request, None, MockObject()
        ) is False


class TestIsAdmin:
    """Test IsAdmin permission class.

    :author: claude
    """

    def test_admin_user_has_permission(
        self, factory, user_admin
    ):
        """Admin user (role='admin') has permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_admin
        permission = IsAdmin()
        assert permission.has_permission(request, None) is True

    def test_regular_user_denied(
        self, factory, user_regular
    ):
        """Regular user denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = IsAdmin()
        assert permission.has_permission(request, None) is False

    def test_anonymous_denied(self, factory):
        """Anonymous user denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = AnonymousUser()
        permission = IsAdmin()
        assert permission.has_permission(request, None) is False

    def test_moderator_denied(
        self, factory, user_moderator
    ):
        """Moderator user denied (not admin).

        :author: claude
        """
        request = factory.get('/')
        request.user = user_moderator
        permission = IsAdmin()
        assert permission.has_permission(request, None) is False

    def test_admin_object_permission(
        self, factory, user_admin
    ):
        """Admin user has object permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_admin
        permission = IsAdmin()
        assert permission.has_object_permission(
            request, None, None
        ) is True

    def test_non_admin_object_permission_denied(
        self, factory, user_regular
    ):
        """Non-admin user denied object permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = IsAdmin()
        assert permission.has_object_permission(
            request, None, None
        ) is False


class TestIsModerator:
    """Test IsModerator permission class.

    :author: claude
    """

    def test_moderator_has_permission(
        self, factory, user_moderator
    ):
        """Moderator user has permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_moderator
        permission = IsModerator()
        assert permission.has_permission(request, None) is True

    def test_regular_user_denied(
        self, factory, user_regular
    ):
        """Regular user denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = IsModerator()
        assert permission.has_permission(request, None) is False

    def test_anonymous_denied(self, factory):
        """Anonymous user denied.

        :author: claude
        """
        request = factory.get('/')
        request.user = AnonymousUser()
        permission = IsModerator()
        assert permission.has_permission(request, None) is False

    def test_admin_denied(
        self, factory, user_admin
    ):
        """Admin user denied (only moderator allowed).

        :author: claude
        """
        request = factory.get('/')
        request.user = user_admin
        permission = IsModerator()
        assert permission.has_permission(request, None) is False

    def test_moderator_object_permission(
        self, factory, user_moderator
    ):
        """Moderator user has object permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_moderator
        permission = IsModerator()
        assert permission.has_object_permission(
            request, None, None
        ) is True

    def test_non_moderator_object_permission_denied(
        self, factory, user_regular
    ):
        """Non-moderator user denied object permission.

        :author: claude
        """
        request = factory.get('/')
        request.user = user_regular
        permission = IsModerator()
        assert permission.has_object_permission(
            request, None, None
        ) is False
