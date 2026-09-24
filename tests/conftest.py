import os
import sys

# Add the backend project root to Python's import path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application configured for testing.
    """

    test_database_url = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )

    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=test_database_url,
        JWT_SECRET_KEY="test-jwt-secret-key"
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """
    Flask test client.
    """

    return app.test_client()


@pytest.fixture()
def database(app):
    """
    Database session available to individual tests.
    """

    with app.app_context():
        yield db.session

        db.session.rollback()