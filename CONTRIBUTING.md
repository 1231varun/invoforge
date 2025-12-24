# Contributing to InvoForge

First off, thank you for considering contributing to InvoForge! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Versioning](#versioning)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

Be kind, respectful, and constructive. We're all here to build something useful for freelancers.

## How Can I Contribute?

### 🐛 Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/1231varun/invoforge/issues)
2. If not, create a new issue using the [Bug Report template](https://github.com/1231varun/invoforge/issues/new?template=bug_report.md)
3. Include as much detail as possible

### 💡 Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue using the [Feature Request template](https://github.com/1231varun/invoforge/issues/new?template=feature_request.md)
3. Explain why this feature would be useful

### 🔧 Code Contributions

1. Look for issues labeled `good first issue` or `help wanted`
2. Comment on the issue to let others know you're working on it
3. Fork, code, and submit a PR!

## Development Setup

### Prerequisites

- Python 3.9+
- LibreOffice (optional, for PDF conversion)

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/invoforge.git
cd invoforge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

Open http://127.0.0.1:5665 in your browser.

### Key Commands

| Command | Description |
|---------|-------------|
| `python run.py` | Run development server on port 5665 |
| `python build_app.py` | Build standalone executable |

## Project Structure

InvoForge follows **Clean Architecture**:

```
invoforge/
├── app/
│   ├── core/                    # Domain Layer (no external dependencies)
│   │   ├── entities/            # Invoice, Leave, Settings dataclasses
│   │   ├── interfaces/          # Abstract repository/service ports
│   │   └── services/            # Business logic (calculators)
│   ├── application/             # Use Cases Layer
│   │   └── use_cases/           # Orchestrates domain logic
│   ├── infrastructure/          # External Implementations
│   │   ├── persistence/         # SQLite repositories
│   │   └── documents/           # DOCX/PDF generators
│   ├── presentation/            # Web Layer
│   │   └── routes/              # Flask API endpoints
│   ├── templates/               # Jinja2 HTML templates
│   ├── container.py             # Dependency injection
│   └── version.py               # App version
├── static/
│   ├── css/styles.css           # All styles (CSS variables for theming)
│   ├── js/app.js                # Frontend JavaScript
│   └── sw.js                    # Service Worker (PWA)
├── data/                        # SQLite database (gitignored)
├── output/                      # Generated invoices (gitignored)
└── .github/
    ├── workflows/               # CI/CD pipelines
    └── ISSUE_TEMPLATE/          # Bug/feature templates
```

**Key Principle**: Dependencies point inward. Core has no external dependencies.

## Versioning

InvoForge uses [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH (e.g., 0.1.0)
```

| Version | When to bump |
|---------|--------------|
| MAJOR | Breaking changes, major rewrites |
| MINOR | New features (backwards compatible) |
| PATCH | Bug fixes |

### Version Files

There are **two types of versions** to manage:

| Version | Files | Purpose |
|---------|-------|---------|
| **APP_VERSION** | `app/version.py`, `static/sw.js` | Semantic version for releases |
| **CACHE_VERSION** | `static/sw.js` | PWA cache - bump when CSS/JS changes |

### Updating Versions

When releasing a new version:

1. Update `app/version.py`:
   ```python
   __version__ = "0.2.0"
   __version_info__ = (0, 2, 0)
   ```

2. Update `static/sw.js`:
   ```javascript
   const APP_VERSION = '0.2.0';
   const CACHE_VERSION = 'v2';  // Bump if static files changed
   ```

3. Update `CHANGELOG.md` with release notes

4. Commit, tag, and push:
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

### CSS Versioning

When you change CSS/JS files, bump the query string in templates:

```html
<!-- In index.html and setup.html -->
<link rel="stylesheet" href="/static/css/styles.css?v=14">
<script src="/static/js/app.js?v=5"></script>
```

This forces browsers to reload the updated files.

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear, concise commits
4. **Test your changes** thoroughly
5. **Push** to your fork: `git push origin feature/amazing-feature`
6. **Open a Pull Request** against the `main` branch

### PR Checklist

- [ ] Code follows the project style guidelines
- [ ] Self-reviewed my code
- [ ] Added comments for complex logic
- [ ] Changes don't break existing functionality
- [ ] Updated version numbers if needed
- [ ] Updated documentation if needed

## Style Guidelines

### Python

- Follow PEP 8
- Use type hints where appropriate
- Keep functions focused and small
- Write docstrings for public functions

```python
def calculate_working_days(year: int, month: int) -> int:
    """Calculate total weekdays in a month."""
    ...
```

### JavaScript

- Use vanilla JS (no frameworks)
- Keep it simple and readable
- Use `const`/`let`, avoid `var`
- Use async/await for API calls

### CSS

- Use CSS custom properties for theming
- Mobile-first responsive design
- Keep specificity low
- Theme variables are in `:root` and `[data-theme="dark"]`

### HTML/Jinja2

- Use semantic HTML
- Keep templates clean
- Use Jinja2 blocks for reusability

### Commits

- Use clear, descriptive commit messages
- Start with a verb: "Add", "Fix", "Update", "Remove"
- Keep commits atomic (one logical change per commit)

Examples:
```
Add multiple client support
Fix PDF generation on Windows
Update dashboard stats calculation
Remove deprecated API endpoint
```

## Testing

InvoForge uses **pytest** for testing. Tests follow the same clean architecture structure.

### Running Tests

```bash
# Install dev dependencies (includes pytest)
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_invoice_calculator.py

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run only unit tests (fast)
pytest tests/unit -v
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
└── unit/                    # Unit tests (fast, no I/O)
    ├── test_amount_formatter.py
    ├── test_entities.py
    ├── test_invoice_calculator.py
    ├── test_use_cases.py
    └── test_working_days_calculator.py
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- Use **fixtures** from `conftest.py` for reusable test data
- Use **mocks** for external dependencies (repositories)
- All test data should use **clearly fake/placeholder values**
- Follow AAA pattern: **A**rrange, **A**ct, **A**ssert

```python
def test_example(self, invoice_calculator: InvoiceCalculator):
    # Arrange
    input_data = InvoiceInput(...)
    
    # Act
    result = invoice_calculator.create_invoice(input_data, "EUR")
    
    # Assert
    assert result.amount == 2100.00
```

## Linting

InvoForge uses **Ruff** for linting and formatting.

### Running Linter

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Check formatting (CI mode)
ruff format --check .
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before commits.

```bash
# Install pre-commit
pip install pre-commit

# Install hooks (one-time)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Hooks will automatically run on `git commit` and check:
- Ruff linting
- Ruff formatting
- Trailing whitespace
- YAML/JSON validity
- Large file prevention

## Questions?

Feel free to open a [Discussion](https://github.com/1231varun/invoforge/discussions) or reach out!

---

Thank you for contributing! ⚒️
