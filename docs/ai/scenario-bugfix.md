# Scenario: Fixing a Bug

This guide describes the workflow for diagnosing and fixing bugs in the YaMDb API.

## When to Apply

Use this scenario when:
- User reports incorrect behavior (wrong HTTP status, exception, malformed response)
- User describes a crash (500 error, unhandled exception)
- User reports validation failure (accepts invalid data, rejects valid data)
- User reports data consistency issue (stale data, race condition)

## Mandatory Order of Actions

### Step 1: Write a Failing Test FIRST

**Before touching production code**, write a pytest test that:
- Reproduces the exact bug described by the user
- Fails with the current code (red test)
- Proves that the bug exists

Example:

```python
def test_duplicate_review_same_user_returns_400():
    """Creating second review for same title by same user returns 400.

    Bug: Currently returns 500 Internal Server Error
    Expected: Returns 400 with validation error message
    
    :author: claude
    """
    title = Title.objects.create(name='Test Title', year=2020)
    user = User.objects.create_user(username='testuser', password='pass')
    
    # Create first review — should succeed
    Review.objects.create(
        title=title, author=user, text='Good movie', score=8
    )
    
    # Try to create second review — should fail with 400
    api_client.force_authenticate(user=user)
    response = api_client.post(
        f'/api/v1/titles/{title.id}/reviews/',
        {'text': 'Another review', 'score': 9}
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.data[0].lower()
```

**Run the test:**
```bash
pytest tests/test_reviews.py::test_duplicate_review_same_user_returns_400 -vv
# Expected: FAILED (red test)
```

### Step 2: Localize the Root Cause

Determine **exactly** where the bug is:
- Read stack trace from test failure
- Identify the file and line number
- Trace through the code logic
- Document your findings

Example findings:
```
Root Cause:
- File: api_yamdb/reviews/models.py, line 142
- Model: Review.save()
- Issue: No validation that prevents duplicate reviews; database IntegrityError bubbles up as 500
- Why: Unique constraint exists in DB, but no model-level or serializer-level validation
```

### Step 3: Fix with Minimal Change

Make only the necessary fix. Do **not**:
- Refactor surrounding code
- Rename variables
- Reorganize imports
- Add "improvements"

Fix strategies (in order of preference):

1. **Serializer validation** — Add `validate()` or field validators
2. **Model constraints** — Add `unique_together`, validators, or property checks
3. **View logic** — Check before `.create()` or catch exceptions
4. **Permissions** — Add custom permission if access control is the issue

Pick the minimal change. In the example:

**Option A (Preferred)**: Add serializer validation
```python
# api/serializers.py
class ReviewSerializer(serializers.ModelSerializer):
    def validate(self, data):
        title = data['title']
        user = self.context['request'].user
        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                'User already has a review for this title.'
            )
        return data
```

**Option B (Alternative)**: Model-level constraint
```python
# reviews/models.py
class Review(models.Model):
    class Meta:
        unique_together = ('title', 'author')
```

Choose based on error message quality and user expectations.

### Step 4: Run Tests

```bash
# Run the failing test — should now pass (green)
pytest tests/test_reviews.py::test_duplicate_review_same_user_returns_400 -vv

# Run all tests in the module — should pass
pytest tests/test_reviews.py -vv

# Run all tests — should pass
pytest tests/ -vv
```

Expected: All green, 0 failures, 0 errors.

### Step 5: Check Code Style

```bash
flake8 api_yamdb/

# Should output: 0 errors/warnings (clean)
```

## Example User Request

> "Баг: при попытке создать второй отзыв на тот же title тем же пользователем сервер падает с 500, ожидается 400 с понятным сообщением."

Translation: "Bug: Creating a second review for the same title by the same user crashes with 500; expected 400 with a clear error message."

## Expected Response Structure

### Plan

Structure showing the 5 mandatory steps:

```
### Plan

1. **Write failing test** — Reproduce duplicate review attempt, expect 400
2. **Localize root cause** — Find where validation is missing
3. **Implement fix** — Add serializer-level validation (preferred) or model constraint
4. **Run tests** — Verify failing test now passes, all others still green
5. **Check flake8** — Ensure no style violations
```

### Changes

Show changes in order: **test first, then fix**

```
tests/test_reviews.py:
- Add test_duplicate_review_same_user_returns_400

api/serializers.py:
- Add validate() method to ReviewSerializer
- Raises ValidationError if Review already exists
```

Provide complete code via tool calls (edits or writes).

### Explanation

Root cause + why this fix (2–3 sentences):

Example:
> "The bug occurred because the serializer had no validation preventing duplicate reviews per user. The database has a unique constraint, but DRF never checked it before hitting the database, causing an IntegrityError (500). The fix adds serializer-level validation to catch duplicates early and return a proper 400 response. Alternative of using `unique_together` in Meta was rejected because it would require a migration and is less flexible for future requirements."

### Verification Steps

```bash
# Confirm the failing test now passes
pytest tests/test_reviews.py::test_duplicate_review_same_user_returns_400 -vv
# Expected: PASSED

# Confirm all review tests pass
pytest tests/test_reviews.py -vv
# Expected: N passed

# Confirm entire test suite passes
pytest tests/ -vv
# Expected: All passed, 0 failed

# Confirm style is clean
flake8 api_yamdb/
# Expected: No output (0 errors)

# Manual test (optional)
http POST http://localhost:8000/api/v1/titles/1/reviews/ \
  text='First review' score:=8 \
  Authorization:"Bearer $TOKEN"
# Response: 201 Created

http POST http://localhost:8000/api/v1/titles/1/reviews/ \
  text='Second review' score:=9 \
  Authorization:"Bearer $TOKEN"
# Response: 400 Bad Request
# {
#   "non_field_errors": ["User already has a review for this title."]
# }
```

## Definition of Done (DoD)

1. ✅ **Test Exists and Catches the Bug**
   - New failing test in `tests/` that reproduces the exact bug
   - Test fails with original code (without the fix)
   - Test passes after the fix is applied

2. ✅ **All Tests Pass**
   - `pytest -vv` shows 100% pass rate
   - No new test failures introduced
   - No existing tests broken

3. ✅ **Code Quality**
   - `flake8 api_yamdb/` returns 0 errors
   - Line length ≤ 79 characters
   - Imports properly organized

4. ✅ **Minimal Change**
   - Only files necessary to fix the bug were edited
   - No refactoring, renaming, or reordering
   - No "while we're here" improvements

5. ✅ **Database Integrity**
   - No new migrations required (unless unavoidable)
   - Existing migrations not modified
   - Fixture files not touched

6. ✅ **Documentation**
   - New test has docstring with `:author: claude`
   - Root cause documented in response explanation
   - If code comments were added, they explain WHY not WHAT

## Workflow: Common Bug Patterns

### Pattern 1: Missing Validation

**User Report**: "API accepts invalid data (negative score, empty text)"

**Fix Location**: Serializer field validators or `validate()` method

```python
# api/serializers.py
class ReviewSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(
        min_value=1, max_value=10,
        error_messages={'min_value': 'Score must be 1–10'}
    )
    text = serializers.CharField(
        min_length=10,
        error_messages={'min_length': 'Review must be at least 10 chars'}
    )
```

### Pattern 2: Missing Permission Check

**User Report**: "Non-admin users can delete other users' reviews"

**Fix Location**: ViewSet permission class or `perform_destroy()` check

```python
# api/views.py
class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]  # or custom logic
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Can only delete own reviews')
        instance.delete()
```

### Pattern 3: Unhandled Exception

**User Report**: "Creating review crashes with 500 if title doesn't exist"

**Fix Location**: View's `perform_create()` or `retrieve()` error handling

```python
# api/views.py
def retrieve(self, request, *args, **kwargs):
    try:
        return super().retrieve(request, *args, **kwargs)
    except Title.DoesNotExist:
        return Response(
            {'detail': 'Title not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
```

### Pattern 4: Race Condition / Concurrent Updates

**User Report**: "Sometimes user role changes are lost; last update wins"

**Fix Location**: Model method with `select_for_update()` or atomic transaction

```python
# reviews/models.py (if needed) or api/views.py
from django.db.models import F
from django.db import transaction

@transaction.atomic
def update_user_role(user_id, new_role):
    user = User.objects.select_for_update().get(id=user_id)
    # Check conditions, update safely
    user.role = new_role
    user.save()
```

### Pattern 5: Pagination / Query Performance

**User Report**: "Loading titles endpoint is very slow"

**Fix Location**: ViewSet `get_queryset()` with `.select_related()` / `.prefetch_related()`

```python
# api/views.py
class TitleViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Title.objects.select_related(
            'category'
        ).prefetch_related(
            'genre'
        ).annotate(
            rating=Avg('reviews__score')
        )
```

## Testing Strategy for Bugs

### Test Structure

```python
class TestReviewValidation:
    def test_duplicate_review_returns_400(self, db, api_client):
        """Duplicate review returns 400 with error message.

        Bug: Was returning 500 IntegrityError
        
        :author: claude
        """
        # Setup: Create title and user
        title = Title.objects.create(name='Movie', year=2020)
        user = User.objects.create_user(username='user', password='pass')
        
        # Action: Create first review
        Review.objects.create(
            title=title, author=user, text='Good', score=8
        )
        
        # Action: Attempt duplicate
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f'/api/v1/titles/{title.id}/reviews/',
            {'text': 'Bad', 'score': 7}
        )
        
        # Assertion: Verify 400 response
        assert response.status_code == 400
        assert 'already' in str(response.data).lower()
```

### Edge Cases to Test

- Boundary values (score 0, 11, empty string, max text length)
- Permission mismatches (user A creates, user B deletes)
- Missing required fields
- Invalid foreign keys (non-existent title)
- Concurrent operations (two requests, same resource)
- State-dependent behavior (can only delete if author)

## When NOT to Fix (Escalate)

If the bug requires **any** of the following, discuss with user first:

1. **Database migration** — Changing schema is complex; confirm intent
2. **API contract change** — Different response format/status code; confirm backward compatibility
3. **Architectural change** — Redesign of permissions, filtering, or data model
4. **New dependencies** — Adding packages not in requirements.txt
5. **Cross-module refactoring** — Changes ripple to multiple apps

## Related Files

- Test templates: `tests/test_*.py`
- Pytest config: `pytest.ini`
- Linting config: `setup.cfg`
- API endpoints: `api_yamdb/api/views.py`, `api_yamdb/api/urls.py`
- Models: `api_yamdb/reviews/models.py`
