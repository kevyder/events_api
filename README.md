
# FastAPI Template

[![CI](https://github.com/kevyder/fastapi_template/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/kevyder/fastapi_template/actions/workflows/ci.yml)

This project is a template for building FastAPI applications with best practices for development, testing, and deployment using Docker and UV.

## Features

- FastAPI application structure
- Docker and Docker Compose support for development and testing
- uv for fast dependency management
- Pre-configured for testing with pytest
- Example endpoints and test cases

## Requirements

- Python 3.13+
- Docker & Docker Compose
- uv (for local development)
  ```sh
  pip install uv
  ```

## Project Structure

```
├── src/
│   └── main.py           # FastAPI application
├── tests/
│   └── test_main.py      # Example pytest test
├── Dockerfile            # Production Docker build
├── docker-compose.yml    # Development container
├── docker-compose.test.yml # Test container
├── pyproject.toml        # Project configuration
├── README.md             # Project documentation
```

## Setup

### Local Development

1. Create and activate virtual environment:
	```sh
	uv venv
	source .venv/bin/activate
	```

2. Install dependencies:
	```sh
	uv pip install -e .[dev,test]
	```

3. Set up pre-commit hooks (recommended):
	```sh
	pre-commit install
	```
	This will install git hooks to automatically run:
	- ruff (code formatting and linting)
	- conventional commit validation

	Pre-commit will run these checks before each commit to ensure code quality.

4. Run the application:
	```sh
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
	```

### Using Docker Compose

Build and start the development server:

```sh
docker-compose up --build
```

The app will be available at http://localhost:8080

## API Endpoints

- `GET /` — Returns a welcome message

## Running Tests

### Locally

With activated virtual environment:
```sh
pytest
```

### With Docker Compose

To run tests in a containerized environment:

```sh
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

This will build the test container and run pytest against your FastAPI project.
