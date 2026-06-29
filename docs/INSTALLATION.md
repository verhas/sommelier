# Installation Guide

## System Requirements

- Python 3.8 or later
- pip (Python package manager)

## Quick Install

Install Sommelier from PyPI:

```bash
pip install sommelier
```

## Verify Installation

Check that Sommelier is installed correctly:

```bash
sommelier --version
```

You should see output like: `sommelier 0.1.0`

## Development Setup

If you want to contribute or modify Sommelier, clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/sommelier.git
cd sommelier
pip install -e ".[dev]"
```

The `[dev]` extra installs additional tools for testing and code formatting:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- black (code formatter)
- flake8 (linter)
- twine (PyPI upload tool)

## First Run

After installation, you can:

1. Generate code from an example:
   ```bash
   sommelier generate examples/java-spring/schema.yaml --dry-run
   ```

2. List available example templates:
   ```bash
   sommelier list-templates
   ```

3. Initialize a new project from a template:
   ```bash
   sommelier init --template java-spring --output my-project
   ```

## Troubleshooting

### Command not found
If `sommelier` command is not found after installation, you may need to add Python's bin directory to your PATH:

- **Linux/macOS**: `~/.local/bin` or `/usr/local/bin`
- **Windows**: `%APPDATA%\Python\Scripts`

### Permission denied (macOS/Linux)
If you get permission errors when installing to system Python, use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install sommelier
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade sommelier
```

## Uninstalling

To remove Sommelier:

```bash
pip uninstall sommelier
```
