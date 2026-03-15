# Agent Guidelines

## Project Overview

Django application for a film festival.

## Build/Lint/Test Commands

```bash
# Development server
uv run manage.py runserver

# Linting (MUST run before committing)
uv run ruff check
uv run djade main/templates/**/*.html --check

# Formatting
uv run ruff format
uv run djade main/templates/**/*.html

# Django management
uv run manage.py <command>

# Database migrations
uv run manage.py makemigrations
uv run manage.py migrate
```

**Note**: There are no tests yet. When adding tests, use Django's test framework:
```bash
# Run all tests
uv run manage.py test

# Run single test
uv run manage.py test main.tests.TestClassName.test_method_name
```

## Code Style Guidelines

### Python

- **Python version**: 3.13+
- **Quotes**: Use double quotes for strings (`"string"`)
- **Line length**: No strict limit (E501 ignored in ruff config)
- **Docstrings**: Use triple double quotes with one-line description for classes/functions
- **Type hints**: Not currently used; add only if explicitly requested

### Imports

- Group order: stdlib, Django, third-party, local
- Within each group: alphabetical order
- Absolute imports for Django modules (`from django.conf import settings`)
- Absolute imports within app (`from main import models; models.Film.objects()...`)

Example:
```python
import os

from django.conf import settings
from django.shortcuts import get_object_or_404

import stripe

from main import models
```

### Naming Conventions

- **Variables/functions**: `snake_case` (e.g., `book_list`, `get_context_data`)
- **Classes**: `PascalCase` (e.g., `BookListView`, `Order`)
- **Constants**: `UPPER_CASE` (e.g., `STRIPE_API_KEY`)
- **Files**: `snake_case.py`
- **Templates**: `snake_case.html`
- **URL names**: `kebab-case` (e.g., `book-list`, `checkout-success`)

### Django Patterns

- Use class-based views (CBVs) by default
- Use `get_object_or_404()` for object retrieval
- Use reverse URL lookups: `{% url 'books:book-buy' book.pk %}`
- Define `app_name` in URL configs for namespacing
- Models: Define `Meta.ordering`, implement `__str__()`

### Error Handling

- Catch specific exceptions, not bare `except:`
- Return appropriate HTTP status codes in views
- Use `fail_silently=False` for critical email sends

### Templates (Django HTML)

- Use Djade formatter for HTML templates
- 4-space indentation in templates
- Use `{% url %}` tag for all internal links

### CSS Patterns

1. Never add the universal selector, eg:

```css
// DO NOT do this
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

Add margin, padding, or box-sizing rules per selector if needed.

2. Do not group all media queries per width, add them per rule.

```css
// DO NOT do this
.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 3rem;
}

.nav-links {
    display: flex;
    gap: 2.5rem;
}

.hero {
    align-items: center;
    text-align: center;
    padding: 6rem 2rem;
}

.hero-meta {
    display: flex;
    align-items: center;
}

@media (max-width: 768px) {
    .nav {
        padding: 1.5rem 1.5rem;
    }

    .nav-links {
        gap: 1.5rem;
    }

    .hero {
        padding: 5rem 1.5rem;
    }

    .hero-meta {
        flex-direction: column;
        gap: 0.5rem;
    }
}
```

```css
// DO this instead
.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 3rem;
} // no empty line
@media (max-width: 768px) {
    .nav {
        padding: 1.5rem 1.5rem;
    }
}

.nav-links {
    display: flex;
    gap: 2.5rem;
}
@media (max-width: 768px) {
    .nav-links {
        gap: 1.5rem;
    }
}

.hero {
    align-items: center;
    text-align: center;
    padding: 6rem 2rem;
}
@media (max-width: 768px) {
    .hero {
        padding: 5rem 1.5rem;
    }
}

.hero-meta {
    display: flex;
    align-items: center;
}
@media (max-width: 768px) {
    .hero-meta {
        flex-direction: column;
        gap: 0.5rem;
    }
}
```

3. All CSS must be at layout.html. Don't add extra_css template blocks.

## Commit Message Style

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat: add Stripe checkout integration`
- `fix: correct film price display in cart`

## Git Workflow

Never push to the remote repository unless the user explicitly asks you to do so.

When the user says "deploy", they mean commit and push.

## Project Structure

```
filmfestival/       # Django project settings
main/               # Main app (models, views, templates)
main/templates/     # Django HTML templates
deploy/             # Deployment scripts
manage.py           # Django management
pyproject.toml      # Dependencies and tool config
```

## Environment Setup

Copy `.envrc.example` to `.envrc` and configure:
- `LOCALDEV=1` - For development (emails print to console)
- `SECRET_KEY` - Production only
- `HOST` - Production domain
