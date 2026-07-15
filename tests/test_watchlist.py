"""Tests for the CineLog watchlist service."""

import pytest

from app import create_app, db
from models import User, Film
from services.collection_service import FilmNotFoundError
from services.watchlist_service import add_to_watchlist, get_watchlist



@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(
        config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """Create a user for watchlist tests."""
    with app.app_context():
        user = User(
            username="watchlistuser",
            email="watchlist@example.com",
        )
        db.session.add(user)
        db.session.commit()
        return user.id
    
    
@pytest.fixture
def sample_film(app):
    """Create a film for watchlist tests."""
    with app.app_context():
        film = Film(
            title="Paddington 2",
            year=2017,
            genre="Comedy",
        )
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that does not exist should raise FilmNotFoundError.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(
                user_id=sample_user,
                film_id=fake_film_id,
            )

def test_get_watchlist_returns_saved_film(
    app,
    sample_user,
    sample_film,
):
    """
    The watchlist should return the saved film and its visibility.
    """
    with app.app_context():
        add_to_watchlist(
            user_id=sample_user,
            film_id=sample_film,
        )

        watchlist = get_watchlist(sample_user)

        assert len(watchlist) == 1
        assert watchlist[0]["title"] == "Paddington 2"
        assert watchlist[0]["public"] is False