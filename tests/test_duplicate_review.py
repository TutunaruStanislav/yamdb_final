import pytest
from rest_framework.test import APIClient

from reviews.models import Review, Title, User


@pytest.fixture
def api_client_fixture():
    """DRF test client.

    :author: claude
    """
    return APIClient()


@pytest.fixture
def user_regular(db):
    """Create regular user.

    :author: claude
    """
    return User.objects.create_user(
        username='testuser',
        password='pass',
        role='user'
    )


@pytest.fixture
def title_fixture(db):
    """Create test title.

    :author: claude
    """
    return Title.objects.create(
        name='Test Title',
        year=2020,
        description='Test description'
    )


class TestDuplicateReview:
    """Test duplicate review creation bug.

    Bug: Creating second review for same title by same user returns 500
    Expected: Should return 400 with validation error

    :author: claude
    """

    def test_duplicate_review_returns_400_not_500(
        self, api_client_fixture, user_regular, title_fixture
    ):
        """Duplicate review attempt returns 400, not 500.

        Bug: Currently returns 500 IntegrityError
        Expected: Returns 400 with validation error message

        :author: claude
        """
        # Create first review — should succeed
        api_client_fixture.force_authenticate(user=user_regular)
        response1 = api_client_fixture.post(
            f'/api/v1/titles/{title_fixture.id}/reviews/',
            {'text': 'First review', 'score': 8}
        )
        assert response1.status_code == 201

        # Try to create second review — should fail with 400, not 500
        response2 = api_client_fixture.post(
            f'/api/v1/titles/{title_fixture.id}/reviews/',
            {'text': 'Second review', 'score': 9}
        )

        # Should return 400, not 500
        assert response2.status_code == 400, \
            f"Expected 400, got {response2.status_code}. Response: {response2.data}"

        # Should have a clear error message
        error_msg = str(response2.data).lower()
        assert 'уже' in error_msg or 'already' in error_msg
