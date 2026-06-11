# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YaMDb is a Django REST API that aggregates user reviews of creative works (movies, books, etc.). The API provides endpoints for user management, content (titles, genres, categories), and reviews/comments with JWT authentication.

## Architecture

### Core Structure

- **reviews app**: Contains core data models (User, Title, Genre, Category, Review, Comment)
  - `models.py`: All model definitions with custom User model extending AbstractUser
  - `admin.py`: Django admin configuration
  
- **api app**: REST API layer using Django REST Framework
  - `views.py`: ViewSets for each model (UserViewSet, TitleViewSet, etc.) + auth endpoints
  - `serializers.py`: DRF Serializers for validation and representation
  - `permissions.py`: Custom permission classes for authorization
  - `filters.py`: Custom filters for QuerySets
  - `pagination.py`: Pagination configuration
  - `urls.py`: URL routing using DefaultRouter

### Key Design Notes

- **Custom User Model**: `reviews.User` extends `AbstractUser` with additional `bio` and `role` fields (user/moderator/admin roles)
- **Authentication**: JWT via `rest_framework_simplejwt` with 1-day access token lifetime
- **Authorization**: Role-based access control for admin/moderator operations
- **API Versioning**: Routes under `/api/v1/` namespace
- **API Documentation**: ReDoc available at `/redoc/` (generated from docstrings/schema)
- **Pagination**: Default page size is 5 items

### Models Relationship

```
User (custom auth model)
├── Review (on Title)
│   └── Comment
├── Category
├── Genre
└── Title
    ├── Reviews
    ├── Category (FK)
    └── Genres (M2M)
```

## Database

Uses PostgreSQL 13.0 (configured in `settings.py` via env vars). Connection settings:
- `DB_ENGINE`: defaults to `django.db.backends.postgresql`
- `DB_NAME`, `DB_HOST`, `DB_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: all configurable via `.env`

## Development Commands

### Setup (Local Development)

```bash
# Create virtual environment and activate
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies
pip install -r api_yamdb/requirements.txt

# Apply migrations
python api_yamdb/manage.py migrate

# Create superuser for /admin
python api_yamdb/manage.py createsuperuser

# Load fixture data
python api_yamdb/manage.py loaddata fixtures.json
```

### Running Tests

```bash
# All tests
pytest

# Single test file
pytest tests/test_settings.py

# Specific test class or method
pytest tests/test_settings.py::TestSettings::test_settings

# With verbose output (default configured in pytest.ini)
pytest -vv
```

### Linting

```bash
# Check code style (flake8)
flake8 api_yamdb/

# Ignore W503 (line break before binary operator) and exclude migrations/venv
# Configuration in setup.cfg
```

### Django Management

```bash
cd api_yamdb

# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Shell for interactive queries
python manage.py shell

# Load/dump fixtures
python manage.py loaddata fixtures.json
python manage.py dumpdata > fixtures.json
```

### Docker (Production-like Environment)

```bash
cd infra

# Create .env from .env.example
cp .env.example .env

# Build and start containers
docker-compose up -d --build

# Run commands inside web container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py loaddata fixtures.json

# Stop containers
docker-compose down

# View logs
docker-compose logs web
```

## API Endpoints

Base path: `/api/v1/`

### Authentication
- `POST /auth/signup/`: Register new user
- `POST /auth/token/`: Get JWT token (password-based)
- `GET /users/me/`: Get current user profile

### Users (Admin only for most operations)
- `GET/POST /users/`: List/create users
- `GET/PATCH/DELETE /users/{username}/`: User detail/edit/delete

### Titles, Genres, Categories (Read-only for non-admins)
- `GET/POST /titles/`: List/create titles
- `GET/PATCH/DELETE /titles/{id}/`: Title detail/edit/delete
- `GET/POST /genres/`: List/create genres
- `GET/DELETE /genres/{slug}/`: Genre detail/delete
- `GET/POST /categories/`: List/create categories
- `GET/DELETE /categories/{slug}/`: Category detail/delete

### Reviews & Comments
- `GET/POST /titles/{title_id}/reviews/`: List/create reviews
- `GET/PATCH/DELETE /titles/{title_id}/reviews/{review_id}/`: Review detail/edit/delete
- `GET/POST /titles/{title_id}/reviews/{review_id}/comments/`: List/create comments
- `GET/PATCH/DELETE /titles/{title_id}/reviews/{review_id}/comments/{comment_id}/`: Comment detail/edit/delete

## Important Settings

- **DEBUG**: Must be `False` in production (tests verify this)
- **ALLOWED_HOSTS**: Currently hardcoded; needs env var for new deployments
- **SECRET_KEY**: Has default; should be overridden via env var
- **Static Files**: Collected to `/static/` (required before deployment)
- **Media Files**: User-uploaded content stored in `/media/`
- **Email**: File-based backend for development; prints to `sent_emails/` directory

## Testing

Tests are located in `tests/` directory with pytest configuration in `pytest.ini`:
- Test discovery: `test_*.py` files in `tests/` folder
- Settings module: `api_yamdb.settings`
- Verbosity: `-vv` (very verbose) by default
- No cache provider enabled

Common test patterns:
- Model tests: field validation, constraints, relationships
- API tests: endpoint permissions, request/response format, status codes
- Settings tests: deployment-ready configuration checks
- Docker/Infrastructure tests: Dockerfile and docker-compose validation

## Constraints

**Never modify or delete existing migrations** (`api_yamdb/*/migrations/`). Always generate new migrations via `python manage.py makemigrations`. If model changes are needed, create a new migration file.

**Never manually edit fixture files** (`fixtures.json` or any JSON in `fixtures/`). If new test data is required, append new objects to the end of existing fixtures or create a separate fixture file.

**Always generate new migrations for model changes**, never edit existing ones. This ensures database reproducibility across environments and prevents conflicts.

## Communication Style

When a task contains ambiguities (field names, API response format, edge case behavior), ask clarifying questions before implementation — don't make silent assumptions.

When a task is unambiguous, proceed directly to planning and implementation without excessive back-and-forth.

## Code Style

**PEP8 compliance** with maximum line length of **79 characters** (enforced by flake8).

**DRF class naming**: Use `TitleSerializer`, `TitleViewSet` (no Read/Write variants unless explicitly required).

**Import grouping**: stdlib → django/DRF → local imports, separated by blank lines.

**Clean code**: No unused imports, variables, or commented code.

Example:
```python
# stdlib
import json

# django
from django.db import models
from rest_framework import viewsets

# local
from reviews.models import Title
from .serializers import TitleSerializer
```

## Tests Policy

**Every new feature** (endpoint, filter, permission, non-trivial validation) must be accompanied by pytest tests in `tests/`.

**Bugfix workflow**: Write a failing test first (red) that reproduces the bug, then implement the fix (green).

**Pre-submission checks**: Run both `pytest -vv` and `flake8 api_yamdb/` — both must pass.

**Test structure**: Place tests in `tests/test_<module>.py` following existing patterns (test classes, descriptive names).

## Response Format

For each substantive task, structure your response as follows:

1. **Plan** — Numbered list of steps before making any changes
2. **Code Changes** — All edits via tools with explicit file paths
3. **Solution Explanation** — Brief summary: why this approach, alternatives rejected
4. **Verification Steps** — Specific commands (pytest, flake8) and expected results

Example:
```
### Plan
1. Add `approved` field to Review model
2. Generate migration
3. Create reviewer-only permission class
4. Add permission to ReviewUpdateView
5. Write tests for permission enforcement

### Changes
[edits follow here]

### Explanation
Added field to enforce review approval workflow. Alternative of soft-delete was rejected because approval is not a delete operation.

### Verification
pytest tests/test_review_approval.py -vv  # Should pass
flake8 api_yamdb/  # Should pass
```

## Verification Marker

When adding or substantially rewriting a function/method's docstring, include the tag `:author: claude` on its own line at the end of the docstring. This enables grep-based authorship checks.

Example:
```python
def get_average_score(title):
    """Return rounded average review score for a title.

    :author: claude
    """
    scores = title.reviews.values_list('score', flat=True)
    if not scores:
        return None
    return round(sum(scores) / len(scores))
```

**Do not** add this tag to pre-existing docstrings you only read — only to code you write.

## Cross-References

For typical tasks, refer to detailed implementation guides:

- **New endpoint** → `docs/ai/scenario-new-endpoint.md`
- **Module test coverage** → `docs/ai/scenario-add-tests.md`
- **Bugfix workflow** → `docs/ai/scenario-bugfix.md`

After making changes, show the final diff and confirm that existing sections remain unaffected.
