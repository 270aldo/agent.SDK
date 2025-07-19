# Contributing to NGX Voice Sales Agent

Thank you for your interest in contributing to NGX Voice Sales Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- Git

### Setup Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/agent.SDK.git
   cd agent.SDK
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

5. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

Follow our [branching strategy](docs/BRANCHING_STRATEGY.md):

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow our [coding standards](CODING_STANDARDS.md)
- Add comments for complex logic
- Update documentation as needed

### 3. Write Tests

- Add unit tests for new functionality
- Ensure all tests pass:
  ```bash
  ./run_tests.sh all
  ```
- Maintain or improve code coverage

### 4. Lint and Format

Run code quality checks:

```bash
# Python
ruff check src/
ruff format src/
mypy src/

# JavaScript/TypeScript
cd sdk && npm run lint
cd sdk && npm run format
```

### 5. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add amazing new feature"
```

Commit types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Test additions/updates
- `build:` Build system changes
- `ci:` CI/CD changes
- `chore:` Other changes

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Title
Use conventional commit format: `feat: add new feature`

### PR Description
Use our [PR template](.github/PULL_REQUEST_TEMPLATE.md) and include:
- Clear description of changes
- Related issue numbers
- Testing performed
- Screenshots (if UI changes)

### PR Requirements
- All tests must pass
- Code coverage maintained or improved
- No linting errors
- Documentation updated
- Approved by at least one maintainer

## Testing Guidelines

### Unit Tests
Located in `tests/unit/`:
```python
def test_feature_behavior():
    """Test that feature behaves correctly."""
    # Arrange
    service = MyService()
    
    # Act
    result = service.do_something()
    
    # Assert
    assert result == expected_value
```

### Integration Tests
Located in `tests/integration/`:
- Test component interactions
- Use test database
- Mock external services

### Manual Testing
Document manual testing steps in PR description.

## Documentation

### Code Documentation
- Add docstrings to all public functions/classes
- Use Google-style docstrings:
  ```python
  def calculate_roi(revenue: float, cost: float) -> float:
      """Calculate return on investment.
      
      Args:
          revenue: Total revenue generated
          cost: Total cost incurred
          
      Returns:
          ROI as a percentage
          
      Raises:
          ValueError: If cost is zero
      """
  ```

### API Documentation
- Update OpenAPI schemas
- Add examples for new endpoints
- Document error responses

### User Documentation
- Update README.md for major features
- Add guides to `docs/` directory
- Include code examples

## Code Style Guidelines

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 88 (Black default)
- Use descriptive variable names

### JavaScript/TypeScript
- Use ESLint configuration
- Prefer `const` over `let`
- Use async/await over promises
- Document complex logic

### General
- No commented-out code
- No debug print statements
- Handle errors appropriately
- Log important events

## Security Guidelines

- Never commit secrets or API keys
- Use environment variables
- Validate all user inputs
- Follow OWASP guidelines
- Report security issues privately

## Performance Considerations

- Profile before optimizing
- Document performance impacts
- Consider caching strategies
- Optimize database queries
- Monitor memory usage

## Release Process

1. Features merged to `develop`
2. Release branch created
3. Final testing and fixes
4. Merge to `main`
5. Tag with version
6. Deploy to production

## Getting Help

- Check existing issues
- Read documentation
- Ask in discussions
- Contact maintainers

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to NGX Voice Sales Agent!