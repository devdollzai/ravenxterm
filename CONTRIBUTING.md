# Contributing to RavenXTerm

First off, thank you for considering contributing to RavenXTerm! It's people like you that make RavenXTerm such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [RavenXTerm Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [PROJECT EMAIL].

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Request Process

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

### Development Workflow

1. Pick an issue to work on (or create one)
2. Create a feature branch
3. Write your code
4. Write tests for your code
5. Run the test suite
6. Push your branch and create a PR

## Local Development Setup

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/ravenxterm.git
cd ravenxterm
```

2. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Install development dependencies:
```powershell
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```powershell
pre-commit install
```

## Code Style

- Follow PEP 8 style guide for Python code
- Use descriptive variable names
- Comment your code when necessary
- Write docstrings for functions and classes

## Testing

We use pytest for our test suite. To run tests:

```powershell
pytest
```

For coverage report:

```powershell
pytest --cov=ravenxterm tests/
```

## Documentation

- Keep README.md up to date
- Update CHANGELOG.md for notable changes
- Write docstrings for all public interfaces
- Update architecture diagrams when making structural changes

## Making a Contribution

### Reporting Bugs

When reporting bugs, please include:

- Your operating system name and version
- Python version
- Detailed steps to reproduce the bug
- What you expected would happen
- What actually happened

### Suggesting Enhancements

When suggesting enhancements, please include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Any potential alternatives you've considered
- Additional context like screenshots or examples

### First Time Contributors

Look for issues labeled `good first issue` or `help wanted`. These are great starting points for new contributors.

## Community

- Join our Discord server for discussions
- Follow our Twitter for updates
- Subscribe to our newsletter

## Project Structure

```
ravenxterm/
├── docs/               # Documentation
├── ravenxterm/        # Source code
│   ├── core/          # Core functionality
│   ├── models/        # AI model integration
│   ├── terminal/      # Terminal integration
│   └── utils/         # Utilities
├── tests/             # Test suite
├── examples/          # Example usage
└── scripts/           # Development scripts
```

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## Questions?

Don't hesitate to ask for help. Open an issue or reach out to the maintainers directly.

Thank you for contributing to RavenXTerm! 🦅
