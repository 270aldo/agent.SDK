# 📋 NGX Voice Sales Agent - Coding Standards

## Overview

This document defines the coding standards and best practices for the NGX Voice Sales Agent project. All code must adhere to these standards to ensure consistency, maintainability, and quality.

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Standards](#python-standards)
3. [API Design Standards](#api-design-standards)
4. [Database Standards](#database-standards)
5. [Testing Standards](#testing-standards)
6. [Documentation Standards](#documentation-standards)
7. [Git Conventions](#git-conventions)
8. [Security Standards](#security-standards)

## General Principles

### SOLID Principles
- **S**ingle Responsibility: Each class/function should have one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable for base types
- **I**nterface Segregation: Many specific interfaces over general ones
- **D**ependency Inversion: Depend on abstractions, not concretions

### DRY (Don't Repeat Yourself)
- Extract common functionality into shared utilities
- Use configuration over hardcoding
- Create reusable components

### KISS (Keep It Simple, Stupid)
- Prefer simple, readable solutions
- Avoid premature optimization
- Clear code > clever code

## Python Standards

### Code Style
We follow PEP 8 with some additions:
- Line length: 88 characters (Black default)
- Use Black for formatting
- Use isort for import sorting
- Use mypy for type checking

### File Structure
```python
"""Module docstring explaining purpose."""

# Standard library imports
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

# Third-party imports
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from src.domain.entities import User
from src.domain.exceptions import ValidationError
```

### Naming Conventions
```python
# Classes: PascalCase
class UserService:
    pass

# Functions/Variables: snake_case
def calculate_total_price(items: List[Item]) -> Decimal:
    total_price = Decimal("0.00")
    return total_price

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30

# Private: Leading underscore
class Service:
    def __init__(self):
        self._internal_state = {}
    
    def _private_method(self) -> None:
        pass
```

### Type Hints
Always use type hints for function signatures:
```python
from typing import Optional, List, Dict, Union, Tuple, Any
from decimal import Decimal

def process_order(
    order_id: str,
    items: List[Dict[str, Any]],
    discount: Optional[Decimal] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Process an order and return success status.
    
    Args:
        order_id: Unique order identifier
        items: List of order items
        discount: Optional discount amount
        
    Returns:
        Tuple of (success, error_message)
    """
    pass
```

### Error Handling
```python
# ✅ GOOD: Specific exceptions with context
class UserNotFoundError(Exception):
    """Raised when a user is not found in the system."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")

# ✅ GOOD: Proper error handling
async def get_user(user_id: str) -> User:
    try:
        user = await repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user
    except DatabaseError as e:
        logger.error(f"Database error retrieving user {user_id}: {e}")
        raise ServiceUnavailableError("Unable to retrieve user") from e

# ❌ BAD: Catching all exceptions
try:
    # some code
except Exception:
    pass  # Never do this
```

### Async/Await Best Practices
```python
# ✅ GOOD: Proper async context manager
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()

# ✅ GOOD: Concurrent execution
results = await asyncio.gather(
    fetch_user_data(user_id),
    fetch_order_history(user_id),
    fetch_preferences(user_id),
)

# ❌ BAD: Sequential async calls
user = await fetch_user_data(user_id)
orders = await fetch_order_history(user_id)  # Could run concurrently
prefs = await fetch_preferences(user_id)    # Could run concurrently
```

### Dependency Injection
```python
# ✅ GOOD: Constructor injection
class UserService:
    def __init__(
        self,
        repository: UserRepository,
        email_service: EmailService,
        cache: CacheService,
    ) -> None:
        self._repository = repository
        self._email_service = email_service
        self._cache = cache

# ✅ GOOD: Using Protocol for abstraction
from typing import Protocol

class Repository(Protocol):
    async def find_by_id(self, id: str) -> Optional[Entity]:
        ...
    
    async def save(self, entity: Entity) -> None:
        ...
```

## API Design Standards

### RESTful Principles
- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Return appropriate status codes
- Use plural nouns for resources
- Version your APIs

### URL Structure
```
/api/v1/users                 # Collection
/api/v1/users/{id}           # Single resource
/api/v1/users/{id}/orders    # Nested resource
```

### Request/Response Format
```python
# Request model
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.USER
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user"
            }
        }

# Response model
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

### Error Responses
```python
class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "code": "USER_NOT_FOUND",
                "message": "The requested user does not exist",
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
```

## Database Standards

### Naming Conventions
- Tables: Plural, snake_case (e.g., `users`, `order_items`)
- Columns: snake_case (e.g., `created_at`, `user_id`)
- Indexes: `idx_table_column` (e.g., `idx_users_email`)
- Foreign Keys: `fk_table_column` (e.g., `fk_orders_user_id`)
- Constraints: `chk_table_description` (e.g., `chk_users_email_format`)

### Schema Design
```sql
-- ✅ GOOD: Proper constraints and indexes
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_email_format 
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Trigger for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### Query Optimization
```python
# ✅ GOOD: Parameterized queries with specific columns
query = """
    SELECT id, email, name, created_at
    FROM users
    WHERE email = $1 AND deleted_at IS NULL
    LIMIT 1
"""
result = await connection.fetchrow(query, email)

# ❌ BAD: SELECT * and string concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL injection risk!
```

## Testing Standards

### Test Structure
```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.user_service import UserService
from src.domain.exceptions import UserNotFoundError

class TestUserService:
    """Test cases for UserService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance with mocked dependencies."""
        return UserService(repository=mock_repository)
    
    async def test_get_user_success(self, service, mock_repository):
        """Test successful user retrieval."""
        # Arrange
        user_id = "123"
        expected_user = User(id=user_id, email="test@example.com")
        mock_repository.find_by_id.return_value = expected_user
        
        # Act
        result = await service.get_user(user_id)
        
        # Assert
        assert result == expected_user
        mock_repository.find_by_id.assert_called_once_with(user_id)
    
    async def test_get_user_not_found(self, service, mock_repository):
        """Test user not found scenario."""
        # Arrange
        user_id = "999"
        mock_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError) as exc_info:
            await service.get_user(user_id)
        
        assert exc_info.value.user_id == user_id
```

### Test Coverage Requirements
- Minimum 90% code coverage
- 100% coverage for critical business logic
- All edge cases must be tested
- Performance tests for critical paths

## Documentation Standards

### Docstrings (Google Style)
```python
def calculate_roi(
    investment: Decimal,
    returns: Decimal,
    time_period_years: float,
) -> Decimal:
    """
    Calculate Return on Investment (ROI).
    
    Args:
        investment: Initial investment amount
        returns: Total returns from investment
        time_period_years: Investment time period in years
        
    Returns:
        ROI as a decimal percentage (e.g., 0.15 for 15%)
        
    Raises:
        ValueError: If investment is zero or negative
        
    Example:
        >>> calculate_roi(Decimal("1000"), Decimal("1150"), 1.0)
        Decimal("0.15")
    """
    if investment <= 0:
        raise ValueError("Investment must be positive")
    
    return (returns - investment) / investment
```

### Code Comments
```python
# ✅ GOOD: Explains WHY, not WHAT
# Use exponential backoff to avoid overwhelming the service
# during temporary failures
retry_delay = min(base_delay * (2 ** attempt), max_delay)

# ❌ BAD: Obvious comment
# Increment counter by 1
counter += 1
```

## Git Conventions

### Branch Naming
- `feature/NGX-123-user-authentication`
- `bugfix/NGX-456-fix-memory-leak`
- `hotfix/NGX-789-critical-security-patch`
- `chore/update-dependencies`

### Commit Messages
Follow Conventional Commits:
```
type(scope): subject

body

footer
```

Examples:
```
feat(auth): add JWT refresh token support

- Implement refresh token generation
- Add refresh endpoint
- Update token expiration logic

Closes #123

---

fix(api): handle null values in user response

Previously, the API would crash when user profile
fields were null. This fix adds proper null handling
and default values.

Fixes #456
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No security vulnerabilities

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes
```

## Security Standards

### Input Validation
```python
# ✅ GOOD: Validate all inputs
from pydantic import BaseModel, validator, EmailStr

class UserInput(BaseModel):
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    
    @validator('email')
    def validate_email_domain(cls, v):
        blocked_domains = ['tempmail.com', 'throwaway.email']
        domain = v.split('@')[1]
        if domain in blocked_domains:
            raise ValueError('Email domain not allowed')
        return v
```

### Secrets Management
```python
# ✅ GOOD: Use environment variables
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.api_key = os.getenv("API_KEY")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set")

# ❌ BAD: Hardcoded secrets
DATABASE_URL = "postgresql://user:password@localhost/db"  # NEVER!
```

### SQL Injection Prevention
```python
# ✅ GOOD: Parameterized queries
async def get_user_by_email(email: str) -> Optional[User]:
    query = "SELECT * FROM users WHERE email = $1"
    row = await db.fetchrow(query, email)
    return User(**row) if row else None

# ❌ BAD: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL injection!
```

### Authentication & Authorization
```python
# ✅ GOOD: Proper permission checking
from fastapi import Depends, HTTPException, status
from src.auth import get_current_user, User

async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    # Proceed with deletion
```

## Enforcement

These standards are enforced through:
1. Pre-commit hooks (Black, isort, mypy, flake8)
2. CI/CD pipeline checks
3. Code review process
4. Automated security scanning

All code must pass these checks before merging.