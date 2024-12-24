# Database Schema Introspection Tool

A command-line tool for introspecting database schemas and generating documentation.

## Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

The tool currently supports the following commands:

### Introspect Database Schema

```bash
python main.py introspect --conn <connection_string> [options]
```

Options:
- `--conn`: Database connection string (required)
  - Format: `postgresql://user:pass@localhost:5432/mydb`
- `--schema`: Database schema to introspect (default: 'public')
- `--format`: Output format (default: 'json')
- `--output-dir`: Directory to store output files (default: 'output')

Example:
```bash
python main.py introspect --conn postgresql://postgres:postgres@localhost:5432/nestjs --schema public --output-dir ./output
```

To see all available commands:
```bash
python main.py --help
```

To check the version:
```bash
python main.py --version
```

## Development

### Running Tests

The test suite requires a PostgreSQL database. Configure the following environment variables or update the test constants in `tests/test_introspect.py`:

```python
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_NAME = "nestjs"
```

To run tests:
```bash
pytest
```

The test suite includes:
- Basic schema introspection
- Empty schema handling
- Invalid schema handling
- Complex schema with relationships
- Connection error handling

### Project Structure

```
project_root/
|-- src/            # Application source code
|-- tests/          # Test suite
|-- main.py         # CLI entry point
|-- requirements.txt # Dependencies
```
