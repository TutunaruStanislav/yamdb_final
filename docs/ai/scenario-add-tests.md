# Scenario: Adding Tests for Existing Modules

This guide describes the workflow for adding pytest test coverage to existing production code (permissions, filters, ViewSets, model methods).

## When to Apply

Use this scenario when:
- User requests test coverage for an existing module (e.g., `api/permissions.py`, `api/filters.py`)
- User wants to increase coverage of a specific ViewSet or model method
- User asks to test edge cases in a class or function
- Goal is documentation/validation of existing behavior, not new features

## Algorithm

### Step 1: Read and Understand the Target Module

1. Read the entire target file (e.g., `api/permissions.py`)
2. Identify all public classes, functions, and methods
3. Trace logic paths — branches, conditionals, special cases
4. Note dependencies (models, serializers, third-party libraries)

### Step 2: List Test Cases

Write a markdown checklist of test cases **before** writing any test code:

```markdown
### Test Cases for IsAdminOrReadOnly

- [ ] Admin user can perform POST/PATCH/DELETE on any object (happy path)
- [ ] Non-admin user gets 403 on POST request (negative)
- [ ] Non-admin user gets 403 on PATCH request (negative)
- [ ] Non-admin user can GET (read-only, happy path)
- [ ] Anonymous user can GET but not POST (happy path + negative)
- [ ] Moderator is not treated as admin (negative)
```

Include:
- Happy path (valid input/permissions)
- Negative cases (invalid input, insufficient permissions)
- Edge cases (empty data, boundary values, special user roles)
- Integration scenarios (multiple permissions combined)

### Step 3: Agree on Scope

If the list contains **more than 5 test cases** or includes non-obvious scenarios, present it to the user for approval:

> "I've identified 8 test cases for IsAdminOrReadOnly. Should I test all of them, or should we focus on the most critical ones (admin/non-admin/read-only)?"

Wait for user feedback before proceeding.

### Step 4: Write Tests

- Create or append to `tests/test_<module>.py`
- Use existing pytest fixtures (if available in `tests/conftest.py`)
- Each test function should have a clear, descriptive name: `test_<class>_<behavior>_<condition>`
- Add docstring to each test with `:author: claude` tag
- Keep tests independent — no shared state, no test interdependencies

Example test structure:

```python
def test_is_admin_or_readonly_admin_can_post(api_client, user_admin):
    """Admin user can perform POST request.

    :author: claude
    """
    api_client.force_authenticate(user=user_admin)
    response = api_client.post('/api/v1/titles/', {'name': 'Test'})
    assert response.status_code == 201
```

### Step 5: Do NOT Modify Production Code

During test writing:
- Do **not** refactor or fix bugs in production code
- If you discover a bug, document it separately in the output (see "Bugs Found" section below)
- Only write tests for **existing behavior**, even if behavior seems wrong

If a bug is discovered, list it like:

```markdown
### Bugs Found During Testing

1. **IsAdminOrReadOnly** — Moderators are not excluded from write permissions despite not being admins. 
   Expected: Moderators should only have read access.
   Current: Moderators can POST/PATCH like admins.
   (Not fixed in this PR; reported for future review)
```

## Example User Request

> "Покрой тестами api/permissions.py — все кастомные permission-классы."

## Expected Response Structure

### Plan

Present the list of test cases as a markdown checklist:

```
### Plan: Test Coverage for api/permissions.py

Target classes:
- IsAdminOrReadOnly
- IsAdminUser
- IsOwnerOrReadOnly
- IsModerator

#### IsAdminOrReadOnly
- [ ] Admin user can POST/PATCH/DELETE (happy path)
- [ ] Non-admin user gets 403 on POST (negative)
- [ ] Anonymous user can GET (happy path)
- [ ] Read-only methods bypass permission check (happy path)

#### IsAdminUser
- [ ] Admin user has permission (happy path)
- [ ] Non-admin user gets 403 (negative)
- [ ] Moderator user gets 403 (negative)

#### IsOwnerOrReadOnly
- [ ] Owner can PATCH own object (happy path)
- [ ] Non-owner gets 403 on PATCH (negative)
- [ ] Anonymous user can GET (happy path)

#### IsModerator
- [ ] Moderator has permission (happy path)
- [ ] User role gets 403 (negative)
- [ ] Admin gets permission (admin > moderator, happy path)

**Total: 12 test cases** (approved/needs adjustment?)
```

If user says "looks good" or doesn't object, proceed. If >5 cases, ask first.

### Changes

Document all test files created/modified:

```
- tests/test_permissions.py: 12 new tests
  - test_is_admin_or_readonly_admin_can_post
  - test_is_admin_or_readonly_non_admin_cannot_post
  - [... etc ...]
```

Show the complete test file code via tool calls.

### Explanation

Brief summary (2–3 sentences):
- What was tested and why
- What was **not** tested and why (intentional exclusions)
- Any assumptions made about fixtures or test setup

Example:
> "Tested all permission classes with admin/non-admin/moderator/anonymous users. Skipped testing with group-based permissions as YaMDb doesn't use Django groups. Assumed `api_client` and `user_admin` fixtures exist in conftest.py; tests will fail if missing."

### Verification Steps

```bash
# Run the new test file
pytest tests/test_permissions.py -vv

# Expected output: All 12 tests passed
# PASSED tests/test_permissions.py::test_is_admin_or_readonly_admin_can_post
# PASSED tests/test_permissions.py::test_is_admin_or_readonly_non_admin_cannot_post
# ... (12 tests total)

# Check for style issues
flake8 tests/test_permissions.py

# Verify no existing tests were broken
pytest tests/ -vv

# Count total tests
pytest tests/test_permissions.py --collect-only -q
```

Expected result: **12 passed**, 0 failed, 0 skipped.

## Definition of Done (DoD)

1. ✅ **Complete Coverage**
   - Every public class/function has at least one happy-path test
   - Every public class/function has at least one negative/edge-case test
   - Permission classes tested with different user roles (admin/moderator/user/anonymous)

2. ✅ **Test Independence**
   - No test depends on another test's execution order
   - No shared mutable state between tests
   - Fixtures are used to set up clean state for each test

3. ✅ **Code Quality**
   - `pytest -vv tests/test_<module>.py` passes 100% (all tests green)
   - All new tests are actually executed (not skipped, not deselected)
   - `flake8 tests/test_<module>.py` shows no violations
   - Test names are descriptive and follow pattern `test_<class>_<behavior>_<condition>`

4. ✅ **Documentation**
   - Every test function has a docstring
   - Docstrings include `:author: claude` tag on final line
   - Docstring explains what is being tested and expected behavior

5. ✅ **Production Code Unchanged**
   - Zero changes to `api/`, `reviews/` app code
   - If bugs discovered, they are documented separately, not fixed
   - Migrations are not created or modified

## Fixture Usage

### Common Pytest Fixtures (check if they exist)

Look for `tests/conftest.py` or fixture definitions in test files:

```python
# Example fixtures (may vary based on project setup)
@pytest.fixture
def api_client():
    """DRF test client."""
    return APIClient()

@pytest.fixture
def user_admin(db):
    """Create admin user."""
    return User.objects.create_user(
        username='admin', password='admin', role='admin'
    )

@pytest.fixture
def user_regular(db):
    """Create regular user."""
    return User.objects.create_user(
        username='user', password='user', role='user'
    )
```

If fixtures don't exist, create them in the test file or suggest adding them to conftest.py.

## Example: Testing api/filters.py

### Plan

```
### Test Cases for TitleFilter

- [ ] Filter by category slug (happy path)
- [ ] Filter by genre slug (happy path)
- [ ] Filter by year (happy path)
- [ ] Invalid category slug returns empty (negative)
- [ ] Multiple genre filters (AND logic) (happy path)
- [ ] Non-existent genre returns empty (negative)
- [ ] Year filter with invalid value (negative)
- [ ] Combining category + genre + year (integration, happy path)
```

### Changes

```python
# tests/test_filters.py

class TestTitleFilter:
    def test_filter_by_category_slug(self, db, api_client):
        """Filter titles by category slug.

        :author: claude
        """
        category = Category.objects.create(name='Film', slug='film')
        title = Title.objects.create(name='Test', category=category)
        
        response = api_client.get('/api/v1/titles/?category=film')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Test'

    def test_filter_by_invalid_category_slug(self, db, api_client):
        """Invalid category slug returns empty queryset.

        :author: claude
        """
        response = api_client.get('/api/v1/titles/?category=invalid')
        assert response.status_code == 200
        assert len(response.data['results']) == 0
```

### Verification

```bash
pytest tests/test_filters.py::TestTitleFilter -vv

# Expected: 8 tests passed
pytest tests/test_filters.py --collect-only -q
# test_filter_by_category_slug
# test_filter_by_invalid_category_slug
# test_filter_by_genre_slug
# ... (8 total)
```

## Workflow: If You Find a Bug

**During testing, you discover that `IsAdminOrReadOnly` allows moderators to POST.**

In your response:

1. **Do NOT fix it** in production code
2. **Do document it** in a "Bugs Found" section:

```markdown
### Bugs Found During Testing

1. **IsAdminOrReadOnly Permission Check**
   - Issue: Moderators can POST/PATCH despite not being admins
   - Expected: Only admin role should have write access
   - Current Code: `return request.user.is_staff or request.method in SAFE_METHODS`
   - Root Cause: Uses `is_staff` (Django flag) instead of checking `role == 'admin'`
   - Recommendation: Create separate task to fix; not addressed in this PR
```

3. **Write tests that expose the bug**:

```python
def test_is_admin_or_readonly_moderator_cannot_post_bug(api_client, user_moderator):
    """BUG: Moderator can POST (should be read-only).

    Current: Moderator can POST (fails test expectation)
    Expected: Moderator should get 403
    
    :author: claude
    """
    api_client.force_authenticate(user=user_moderator)
    response = api_client.post('/api/v1/titles/', {'name': 'Test'})
    assert response.status_code == 403  # Currently returns 201 (BUG)
```

Mark this test as expected-to-fail if needed, or document it clearly.

## Best Practices

- **Setup vs. Assertion**: Keep setup minimal; assertions clear
- **One assertion per test** (or tightly related assertions): Easier to debug failures
- **Fixture names**: Use descriptive names (`user_admin`, `title_with_reviews`, not `u1`, `t`)
- **Parametrize repetitive tests**: Use `@pytest.mark.parametrize` for similar test cases

Example:
```python
@pytest.mark.parametrize('role,expected_status', [
    ('admin', 201),
    ('moderator', 403),
    ('user', 403),
])
def test_permission_by_role(api_client, role, expected_status):
    """Test permission for different user roles.

    :author: claude
    """
    user = User.objects.create_user(username=role, role=role)
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/v1/titles/', {'name': 'Test'})
    assert response.status_code == expected_status
```

## Related Files

- Test configuration: `pytest.ini`, `setup.cfg`
- Fixtures: `tests/conftest.py` (if exists)
- Example tests: `tests/test_*.py`
- Coverage reports: `pytest --cov=api_yamdb --cov-report=html` (if coverage installed)
