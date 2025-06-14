# Contributing to WolfPy 🐺

Thank you for your interest in contributing to WolfPy! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### 1. Development Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/wolfpy.git
cd wolfpy

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev,all-databases,production]

# Verify installation
wolfpy --version
pytest tests/ -v
```

### 2. Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code, test, document ...

# Run tests and linting
pytest tests/
flake8 src/wolfpy tests
black src/wolfpy tests

# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

## 📋 Contribution Types

We welcome various types of contributions:

### 🐛 Bug Reports
- Use the GitHub issue template
- Include minimal reproduction code
- Specify Python version and OS
- Include error messages and stack traces

### ✨ Feature Requests
- Describe the use case clearly
- Explain why it would benefit users
- Consider backward compatibility
- Provide implementation ideas if possible

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### 📚 Documentation
- API documentation
- Tutorials and guides
- Example applications
- README improvements

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=wolfpy --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest tests/test_core.py -v
pytest tests/test_api.py -v
pytest tests/test_database.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

### Writing Tests

- Write tests for all new functionality
- Aim for >90% code coverage
- Use descriptive test names
- Include edge cases and error conditions
- Use fixtures for common setup

Example test structure:
```python
def test_route_with_parameters():
    """Test that routes with parameters work correctly."""
    app = WolfPy()
    
    @app.route('/user/<int:user_id>')
    def user_profile(request, user_id):
        return f"User {user_id}"
    
    client = TestClient(app)
    response = client.get('/user/123')
    
    assert response.status_code == 200
    assert response.text == "User 123"
```

## 🎨 Code Style Guidelines

### Python Style
- Follow PEP 8 with Black formatting
- Line length: 88 characters
- Use type hints for function signatures
- Write docstrings for public functions

### Code Organization
- Keep functions focused and small
- Use meaningful variable names
- Avoid deep nesting
- Separate concerns clearly

### Documentation Style
- Use Google-style docstrings
- Include examples in docstrings
- Keep documentation up to date
- Use clear, concise language

Example function with proper documentation:
```python
def create_user(username: str, email: str, password: str) -> User:
    """Create a new user with the given credentials.
    
    Args:
        username: Unique username for the user
        email: User's email address
        password: Plain text password (will be hashed)
        
    Returns:
        User: The created user instance
        
    Raises:
        ValidationError: If username or email already exists
        
    Example:
        >>> user = create_user("john", "john@example.com", "secret123")
        >>> print(user.username)
        john
    """
    # Implementation here
```

## 🔄 Pull Request Process

### Before Submitting
1. **Run the full test suite** and ensure all tests pass
2. **Update documentation** if you've changed APIs
3. **Add tests** for new functionality
4. **Run linting tools** and fix any issues
5. **Update CHANGELOG.md** if appropriate

### PR Requirements
- Clear, descriptive title
- Detailed description of changes
- Link to related issues
- Screenshots for UI changes
- Breaking changes clearly marked

### Review Process
1. Automated CI checks must pass
2. At least one maintainer review required
3. Address review feedback promptly
4. Squash commits before merging

## 🏗️ Project Structure

Understanding the codebase structure:

```
wolfpy/
├── src/wolfpy/              # Main package
│   ├── __init__.py         # Package exports
│   ├── app.py              # Main application class
│   ├── core/               # Core framework components
│   │   ├── router.py       # URL routing
│   │   ├── request.py      # Request handling
│   │   ├── response.py     # Response objects
│   │   ├── middleware.py   # Middleware system
│   │   ├── auth.py         # Authentication
│   │   ├── database.py     # Database ORM
│   │   └── template_engine.py # Template rendering
│   ├── cli/                # Command-line interface
│   ├── static/             # Default static files
│   └── templates/          # Default templates
├── tests/                  # Test suite
├── examples/               # Example applications
├── docs/                   # Documentation
└── scripts/                # Build and deployment scripts
```

## 🚀 Release Process

### Version Numbering
We follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release branch
5. Tag release
6. Build and upload to PyPI
7. Create GitHub release

## 🆘 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: Direct contact for sensitive issues

### Resources
- [Documentation](docs/index.md)
- [API Reference](docs/api.md)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)

## 📄 License

By contributing to WolfPy, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to WolfPy! Together we're building something amazing! 🐺✨**
