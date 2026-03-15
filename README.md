# filmfestival

## Development

Run development server:

```sh
uv run manage.py runserver
```
Run linting:

```sh
uv run ruff check
uv run djade main/templates/**/*.html --check
```

Run formatting:

```sh
uv run ruff format
uv run djade main/templates/**/*.html
```

## Commit Message Style

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <description>

[optional body]
```

Types:
- `feat`: new feature
- `fix`: bug fix  
- `docs`: documentation changes
- `style`: formatting (no code changes)
- `refactor`: code refactoring
- `test`: adding tests
- `chore`: maintenance tasks

Examples:
- `feat: add Stripe checkout integration`
- `fix: correct book price display in cart`
- `docs: update deployment instructions`

## License

Copyright sirodoht

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, version 3.
