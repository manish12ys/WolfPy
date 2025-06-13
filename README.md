# WolfPy Web Framework

A lightweight, modular Python web framework built from scratch.

## Features

- **Simple Routing**: Intuitive URL routing with parameter support
- **Template Engine**: Mako template integration with fallback support
- **Database ORM**: SQLite-based ORM with model definitions and migrations
- **Authentication**: Built-in user authentication and session management
- **Middleware**: Flexible middleware system for request/response processing
- **Static Files**: Static file serving and asset management
- **CLI Tools**: Command-line interface for project management
- **Testing**: Comprehensive test suite with pytest integration

## Quick Start

### Installation

```bash
pip install wolfpy
```

### Create a New Project

```bash
wolfpy new myproject
cd myproject
python app.py
```

### Basic Application

```python
from wolfpy import WolfPy
from wolfpy.core.response import Response

app = WolfPy(debug=True)

@app.route('/')
def home(request):
    return "Hello, WolfPy!"

@app.route('/user/<name>')
def user_profile(request, name):
    return f"Hello, {name}!"

@app.route('/api/data', methods=['POST'])
def api_data(request):
    if request.is_json():
        data = request.json
        return Response.json({'received': data})
    return Response.bad_request('JSON required')

if __name__ == '__main__':
    app.run()
```

## Core Components

### Routing

FoxPy provides a flexible routing system with support for:
- Static routes: `/about`, `/contact`
- Dynamic routes: `/user/<name>`, `/post/<int:id>`
- HTTP methods: `GET`, `POST`, `PUT`, `DELETE`, etc.

```python
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_handler(request, user_id):
    if request.method == 'GET':
        return f"User ID: {user_id}"
    elif request.method == 'POST':
        return "User updated"
```

### Database ORM

Simple SQLite-based ORM with model definitions:

```python
from wolfpy.core.database import Model, StringField, IntegerField, DateTimeField

class User(Model):
    id = IntegerField(primary_key=True)
    username = StringField(max_length=50, unique=True)
    email = StringField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)

# Create tables
db.create_tables(User)

# Create and save a user
user = User(username='john', email='john@example.com')
user.save()

# Query users
users = db.objects(User).filter(username='john').all()
```

### Templates

Mako template integration with automatic fallback:

```python
@app.route('/')
def home(request):
    return app.template_engine.render('home.html', {
        'title': 'Welcome',
        'users': users
    })
```

### Authentication

Built-in authentication system:

```python
from foxpy.core.auth import Auth, login_required

auth = Auth(secret_key='your-secret-key')

@app.route('/protected')
@login_required(auth)
def protected_route(request):
    return f"Hello, {request.user.username}!"
```

### REST API System (Phase 6)

Enhanced REST API functionality with decorators and helpers:

```python
from wolfpy import get_route, post_route, put_route, delete_route, Response

@get_route('/api/users')
def list_users(request):
    return paginate_data(users, page=1, per_page=10)

@post_route('/api/users')
def create_user(request):
    # request.api_data contains automatically parsed JSON
    validation_error = validate_required_fields(request.api_data, ['name', 'email'])
    if validation_error:
        return validation_error

    return Response.api_success(new_user, "User created successfully")

@delete_route('/api/users/<int:user_id>')
def delete_user(request, user_id):
    # Returns 204 No Content automatically
    return None
```

Features:
- **JSON Response Helpers**: `api_success()`, `api_error()`, `paginated_response()`
- **Route Decorators**: `@get_route()`, `@post_route()`, `@put_route()`, `@delete_route()`
- **Status Code Customization**: Comprehensive HTTP status code support
- **Validation Helpers**: `validate_required_fields()`, automatic JSON parsing
- **APIRouter**: Organized route management with prefixes

### Middleware

Flexible middleware system:

```python
from wolfpy.core.middleware import CORSMiddleware, LoggingMiddleware

app.add_middleware(CORSMiddleware())
app.add_middleware(LoggingMiddleware())
```

## CLI Commands

WolfPy includes a command-line interface for common tasks:

```bash
# Create a new project
wolfpy new myproject

# Serve an application
wolfpy serve --app app.py --host 0.0.0.0 --port 8000 --debug

# Generate a new route
wolfpy route user_profile --path "/user/<name>" --methods GET POST

# Show application routes
wolfpy routes --app app.py

# Show version
wolfpy version
```

## Examples

The framework includes example applications:

- **Blog**: Complete blog application with authentication and CRUD operations
- **Todo**: RESTful API todo application with JSON responses

Run the examples:

```bash
# Blog example
cd examples/blog
python app.py

# Todo API example
cd examples/todo
python app.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
wolfpy/
├── src/wolfpy/         # Main package
│   ├── core/           # Core components
│   ├── static/         # Default static files
│   └── templates/      # Default templates
├── cli/                # Command-line interface
├── tests/              # Test suite
├── examples/           # Example applications
└── docs/               # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [x] Core routing and WSGI interface
- [x] Template engine integration
- [x] Database ORM
- [x] Authentication system
- [x] Middleware support
- [x] CLI tools
- [x] REST API System (Phase 6)
- [ ] Async/ASGI support
- [ ] WebSocket support
- [ ] Plugin system
- [ ] Admin interface
- [ ] Production deployment tools

## Support

- Documentation: [wolfpy.readthedocs.io](https://wolfpy.readthedocs.io)
- Issues: [GitHub Issues](https://github.com/manish/wolfpy/issues)
- Discussions: [GitHub Discussions](https://github.com/manish/wolfpy/discussions)
