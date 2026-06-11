# Scenario: Adding a New Endpoint

This guide describes the workflow for adding new endpoints, filters, or actions to the YaMDb REST API.

## When to Apply

Use this scenario when:
- Adding a new URL pattern under `/api/v1/`
- Adding a filter or custom `@action` to an existing ViewSet
- Adding a new field to a serializer with custom logic
- Modifying endpoint behavior (permissions, response format, filtering)

## Change Checklist

- [ ] **Model/Migration** — Add model field (if required); generate migration via `python manage.py makemigrations`
- [ ] **Serializer** (`api/serializers.py`) — Add/modify serializer fields and validation
- [ ] **View/Action** (`api/views.py`) — Add ViewSet method, `@action` decorator, or custom endpoint
- [ ] **Permission** (`api/permissions.py`) — Create permission class if access rules differ from defaults
- [ ] **Filter** (`api/filters.py`) — Add filterset or custom filter method (if applicable)
- [ ] **URL Registration** (`api/urls.py`) — Register in DefaultRouter or urlpatterns
- [ ] **Tests** (`tests/`) — Write pytest tests for happy path + edge cases/permissions
- [ ] **Documentation** — Update docstring with `:author: claude` tag

## Example User Request

> "Add endpoint `GET /api/v1/titles/top/` — top 10 titles by average rating, accessible to all, support `?category=<slug>` filter."

## Expected Response Structure

When the user requests a new endpoint, structure your response as follows:

### Plan

Numbered list of implementation steps:

```
### Plan

1. Identify if new model fields are required; if so, create migration
2. Add/modify serializer in api/serializers.py
3. Add custom @action method to ViewSet in api/views.py
4. Create permission class if needed in api/permissions.py
5. Add filter/filterset in api/filters.py if applicable
6. Register endpoint in api/urls.py
7. Write tests in tests/test_<feature>.py
8. Update docstrings with :author: claude tag
```

### Changes

Document all file edits using tool calls with explicit file paths:

```
- api/serializers.py: Add TitleTopSerializer
- api/views.py: Add @action method to TitleViewSet
- api/filters.py: Extend TitleFilter for category support
- tests/test_titles.py: Add test_titles_top_list_success, test_titles_top_filter_by_category
```

### Explanation

Brief justification (2–3 sentences):
- Why this approach
- Alternatives considered and rejected

Example:
> "Used `@action` decorator on TitleViewSet rather than separate endpoint because it keeps related logic grouped. Considered query parameters for sorting but decided on database-level ordering for performance."

### Verification Steps

Concrete commands with expected outcomes:

```bash
# Run tests for the feature
pytest tests/test_titles.py::test_titles_top_list_success -vv

# Check code style
flake8 api_yamdb/api/

# Manual test with httpie
http GET http://localhost:8000/api/v1/titles/top/ category==film

# Expected response: HTTP 200, JSON array of top 10 titles sorted by rating
```

## Definition of Done (DoD)

An endpoint is ready when:

1. ✅ **Endpoint responds correctly**
   - Returns correct HTTP status codes (200, 201, 400, 403, 404, etc.)
   - Response body matches specified format (JSON structure, field names)
   - Filtering, pagination, ordering work as specified

2. ✅ **Tests cover the feature**
   - At least one happy-path test (e.g., valid request succeeds)
   - At least one test for permissions (e.g., unauthorized user gets 403)
   - At least one test for edge cases (e.g., empty results, invalid filter values)
   - All tests use descriptive names and docstrings

3. ✅ **Code quality**
   - `pytest -vv` passes all tests (no failures or errors)
   - `flake8 api_yamdb/` shows no violations
   - Line length ≤ 79 characters
   - Imports organized: stdlib → django/DRF → local

4. ✅ **Documentation**
   - All new functions/methods have docstrings
   - Docstrings include `:author: claude` tag on last line
   - Comments explain non-obvious logic (e.g., specific validation rules)

5. ✅ **Database integrity**
   - Existing migrations in `api_yamdb/*/migrations/` are unmodified
   - New migrations are generated (never hand-edited)
   - Fixture files (`fixtures.json`) are unmodified

## Workflow Example

### User Request
```
Add a custom @action endpoint GET /api/v1/titles/{id}/reviews/summary/ 
that returns:
{
  "total_reviews": <int>,
  "average_rating": <float>,
  "review_count_by_score": {1: <int>, 2: <int>, ..., 10: <int>}
}
Accessible to all (unauthenticated + authenticated).
```

### Clarification Questions (if needed)
- Should unauthenticated users see the summary? (Assuming yes based on "accessible to all")
- Round average_rating to how many decimal places? (Assuming 2)
- Include only approved reviews or all? (Assuming all unless validation rule exists)

### Plan
1. Add method to TitleViewSet with `@action(detail=True, methods=['get'])`
2. Create custom permission class allowing AllowAny
3. Implement aggregation logic using Django ORM (Count, Avg, etc.)
4. Write tests: happy path + permission check
5. Verify flake8 and pytest

### Changes
[edits to views.py, permissions.py, tests/test_titles.py]

### Explanation
Used `@action` to attach logic to TitleViewSet (co-located with retrieve/list). AllowAny permission allows both authenticated and unauthenticated access. Used Django ORM aggregation (F, Case/When) rather than Python loops for database efficiency.

### Verification
```bash
pytest tests/test_titles.py::test_title_reviews_summary -vv
flake8 api_yamdb/api/views.py
http GET http://localhost:8000/api/v1/titles/1/reviews/summary/
```

## Key Constraints

- **Never edit existing migrations** — only create new ones
- **Never edit fixtures manually** — append to end or create new file
- **Always test** — every new endpoint needs at least 2–3 tests
- **Always lint** — `flake8 api_yamdb/` must pass before submission
- **Always document** — docstrings with `:author: claude` for new code

## Related Files

- Main API routing: `api_yamdb/api/urls.py`
- DRF configuration: `api_yamdb/api_yamdb/settings.py` (REST_FRAMEWORK section)
- Test setup: `pytest.ini`, `tests/conftest.py` (if exists)
- Linting rules: `setup.cfg`
