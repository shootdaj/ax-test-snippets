"""Shared test fixtures."""

import pytest
from api.app import create_app
from api import store


@pytest.fixture(autouse=True)
def clean_store():
    """Reset in-memory store before each test."""
    store.reset()
    yield
    store.reset()


@pytest.fixture
def app():
    """Create test application."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_snippet():
    """Create a sample snippet and return it."""
    return store.create_snippet({
        "title": "Hello World",
        "description": "A simple hello world example",
        "code": "print('Hello, World!')",
        "language": "python",
        "filename": "hello.py",
        "tags": ["example", "beginner"],
        "visibility": "public",
    })


@pytest.fixture
def sample_collection():
    """Create a sample collection and return it."""
    return store.create_collection({
        "name": "Python Utils",
        "description": "Useful Python utilities",
    })
