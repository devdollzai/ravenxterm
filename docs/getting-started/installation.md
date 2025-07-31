# Installation

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (optional, for development)

## Installation Methods

### From PyPI (Recommended)

```bash
pip install ravenxterm
```

### From Source

```bash
# Clone the repository
git clone https://github.com/devdollzai/ravenxterm.git

# Navigate to the project directory
cd ravenxterm

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

## Verifying Installation

After installation, verify that RavenXTerm is working correctly:

```bash
ravenxterm --version
```

## Configuration

1. Create a configuration directory:
```bash
mkdir ~/.ravenxterm
```

2. Copy the default configuration:
```bash
ravenxterm --init-config
```

3. Edit the configuration file at `~/.ravenxterm/config.yaml` according to your needs.

## Next Steps

- Read the [Quick Start Guide](../getting-started/quickstart.md) to begin using RavenXTerm
- Learn about [Configuration Options](../getting-started/configuration.md)
- Explore [Advanced Features](../user-guide/advanced-features.md)
