# Quick Start Guide

## Starting RavenXTerm

After [installation](installation.md), you can start RavenXTerm by running:

```bash
ravenxterm
```

## Basic Usage

### Getting Help with Commands

To get help with a command, use the `?` prefix:

```bash
? how to use docker compose
```

### Executing Commands with Explanation

To execute a command with explanation:

```bash
explain tar -czf archive.tar.gz /path/to/directory
```

### Generating Commands from Natural Language

To generate a command based on natural language:

```bash
generate "create a backup of my MySQL database"
```

## Common Operations

### Command History Navigation

- Use ↑ and ↓ arrows to navigate through command history
- Use Ctrl+R to search command history
- Type `history` to see full command history

### Context-Aware Suggestions

RavenXTerm provides context-aware suggestions based on:
- Current directory contents
- Command history
- Project-specific patterns

### Environment Detection

RavenXTerm automatically detects:
- Current shell environment
- Available tools and commands
- Project-specific settings

## Next Steps

- Learn about [Configuration](configuration.md)
- Explore [Advanced Features](../user-guide/advanced-features.md)
- Read the [Architecture Overview](../technical/architecture.md)
