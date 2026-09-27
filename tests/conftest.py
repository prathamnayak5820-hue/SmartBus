
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    test_database_url = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )

    app = create_app({
        "TESTING": True,
        "ALLOW_TEST_ROLE_REGISTRATION": True,
        "SQLALCHEMY_DATABASE_URI": test_database_url,
        "JWT_SECRET_KEY": "test-jwt-secret-key-for-local-tests-only-32",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database(app):
    with app.app_context():
        yield db.session
        db.session.rollback()