# RavenXTerm 🦅

A Local-First AI Terminal Extension with seamless integration into your terminal environment, powered by LLama2 for intelligent command-line assistance.

## Features

- 🚀 **Local-First Operation**: All AI processing happens on your machine, ensuring privacy and offline capability
- 🔒 **Privacy-Focused**: No data leaves your system - all interactions stay local
- ⚡ **Low Latency**: Direct integration with LLama2 for rapid responses
- 🧠 **Context-Aware**: Understands your terminal environment and command history
- 🛠️ **Extensible**: Plug-in architecture for custom command handlers and AI models
- 🎯 **Adaptive Model Selection**: Intelligent model choice based on task requirements and system capabilities
- 📊 **Performance Optimization**: Learns from usage patterns to improve model selection over time
- 💻 **Hardware-Aware**: Automatically detects and utilizes available hardware capabilities (CPU, GPU, NPU)
- ⚙️ **Customizable Preferences**: Fine-tune memory usage, performance modes, and hardware utilization

## Architecture

```ascii
+------------------+     +------------------+     +----------------------+
|                  |     |                  |     |                      |
|  Terminal        |     |  RavenXTerm      |     |  Local LLama2       |
|  Environment     |<--->|  Integration     |<--->|  Model              |
|  (Unix/Windows)  |     |  Layer           |     |  (AI Processing)    |
|                  |     |                  |     |                      |
+------------------+     +------------------+     +----------------------+
         |                       |                         |
         |                       |                         |
         v                       v                         v
+------------------+     +------------------+     +----------------------+
|  Command         |     |  Context         |     |  Model              |
|  History &       |     |  Management      |     |  Cache &            |
|  Environment     |     |  System          |     |  Updates            |
+------------------+     +------------------+     +----------------------+

```

## Local-First AI Flow

1. **User Input**: Commands and queries are captured in the terminal
2. **Context Collection**: Local environment data and command history are gathered
3. **Local Processing**: LLama2 model processes the input entirely on your machine
4. **Response Generation**: AI generates contextually relevant responses
5. **Terminal Integration**: Results are seamlessly displayed in your terminal

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ravenxterm.git

# Navigate to the project directory
cd ravenxterm

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py install
```

## Usage

```bash
# Start RavenXTerm
ravenxterm

# Get help with a command
? how to use docker compose

# Execute a complex command with explanation
explain tar -czf archive.tar.gz /path/to/directory

# Generate a command based on natural language
generate "create a backup of my MySQL database"

# Configure model preferences
ravenxterm config set performance_mode speed
ravenxterm config set accuracy high

# View system status and model performance
ravenxterm status
ravenxterm models list
```

## Model Management

RavenXTerm includes a sophisticated model management system that handles:

- **Automatic Model Selection**: Chooses the best model based on task requirements and available resources
- **Performance Tracking**: Monitors and learns from model performance to improve selection
- **Resource Management**: Efficiently manages memory usage and hardware utilization
- **Adaptive Learning**: Continuously improves model selection based on usage patterns

### Configuration Options

```yaml
model:
  performance_mode: speed  # speed, memory, or balanced
  accuracy_preference: high  # high, medium, or low
  max_memory_usage: 0.7  # Fraction of system memory to use
  preferred_devices:
    - cuda  # Use GPU if available
    - cpu  # Fallback to CPU

cache:
  enabled: true
  max_size_gb: 10
  cleanup_threshold: 0.8  # Cleanup when 80% full
```

## Configuration

RavenXTerm can be configured through `~/.ravenxterm/config.yaml`:

```yaml
model:
  path: ~/.ravenxterm/models/llama2
  type: llama2
  context_length: 2048

terminal:
  history_size: 1000
  theme: dark
  prompt_style: minimal
```

## Development

### Prerequisites

- Python 3.8+
- PyTorch
- Node.js 16+

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing to the project.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
