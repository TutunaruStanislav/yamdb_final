import pytest
from rest_framework.test import APIClient

from reviews.models import Category, Review, Title, User


@pytest.fixture
def api_client_fixture():
    """DRF test client.

    :author: claude
    """
    return APIClient()


@pytest.fixture
def category_fixture(db):
    """Create test category.

    :author: claude
    """
    return Category.objects.create(name='Film', slug='film')


@pytest.fixture
def titles_with_ratings(db, category_fixture):
    """Create 15 titles with varying ratings.

    :author: claude
    """
    titles = []
    for i in range(1, 16):
        title = Title.objects.create(
            name=f'Title {i}',
            year=2020 + i,
            category=category_fixture,
            description=f'Description {i}'
        )
        titles.append(title)

    users = [
        User.objects.create_user(
            username=f'user{j}', password='pass'
        ) for j in range(1, 6)
    ]

    for idx, title in enumerate(titles):
        score = 10 - (idx % 10)
        Review.objects.create(
            title=title,
            author=users[idx % 5],
            text=f'Review for title {title.id}',
            score=score
        )

    return titles


class TestTitlesTopEndpoint:
    def test_titles_top_returns_200_anonymous(
        self, api_client_fixture, titles_with_ratings
    ):
        """GET /api/v1/titles/top/ returns 200 for anonymous user.

        :author: claude
        """
        response = api_client_fixture.get('/api/v1/titles/top/')
        assert response.status_code == 200

    def test_titles_top_returns_list(
        self, api_client_fixture, titles_with_ratings
    ):
        """GET /api/v1/titles/top/ returns paginated list of titles.

        :author: claude
        """
        response = api_client_fixture.get('/api/v1/titles/top/')
        assert response.status_code == 200
        assert 'results' in response.data or isinstance(
            response.data, list
        )

    def test_titles_top_limits_to_10(
        self, api_client_fixture, titles_with_ratings
    ):
        """GET /api/v1/titles/top/ returns at most 10 titles.

        :author: claude
        """
        response = api_client_fixture.get('/api/v1/titles/top/')
        results = (
            response.data.get('results', response.data)
            if isinstance(response.data, dict) else response.data
        )
        assert len(results) <= 10

    def test_titles_top_sorted_by_rating_desc(
        self, api_client_fixture, titles_with_ratings
    ):
        """GET /api/v1/titles/top/ sorts by rating descending.

        :author: claude
        """
        response = api_client_fixture.get('/api/v1/titles/top/')
        results = (
            response.data.get('results', response.data)
            if isinstance(response.data, dict) else response.data
        )

        ratings = [item.get('rating') for item in results]
        assert ratings == sorted(ratings, reverse=True)

    def test_titles_top_filter_by_category(
        self, api_client_fixture, db
    ):
        """GET /api/v1/titles/top/?category=<slug> filters by category.

        :author: claude
        """
        film = Category.objects.create(name='Film', slug='film')
        book = Category.objects.create(name='Book', slug='book')

        film_title = Title.objects.create(
            name='Film Title',
            year=2020,
            category=film
        )
        book_title = Title.objects.create(
            name='Book Title',
            year=2020,
            category=book
        )

        user = User.objects.create_user(username='user1', password='pass')
        Review.objects.create(
            title=film_title, author=user,
            text='Review', score=9
        )
        Review.objects.create(
            title=book_title, author=user,
            text='Review', score=8
        )

        response = api_client_fixture.get(
            '/api/v1/titles/top/?category=film'
        )
        results = (
            response.data.get('results', response.data)
            if isinstance(response.data, dict) else response.data
        )

        assert len(results) >= 1
        assert results[0]['name'] == 'Film Title'

    def test_titles_top_handles_empty_results(
        self, api_client_fixture, db
    ):
        """GET /api/v1/titles/top/ returns empty list if no titles.

        :author: claude
        """
        response = api_client_fixture.get('/api/v1/titles/top/')
        results = (
            response.data.get('results', response.data)
            if isinstance(response.data, dict) else response.data
        )
        assert isinstance(results, list)
        assert len(results) == 0
