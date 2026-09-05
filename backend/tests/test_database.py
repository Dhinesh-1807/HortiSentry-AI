from sqlalchemy import text
from app.models.models import Crop, ModelVersion, User

def test_database_connection(db_session):
    """Verify raw SQL execution on test SQLite session."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

def test_database_models_creation(db_session):
    """Verify ORM model creation and querying using UUID IDs."""
    test_user = User(
        role="FARMER",
        name="Test Farmer",
        email="testfarmer@hortisentry.org"
    )
    db_session.add(test_user)
    db_session.commit()

    fetched = db_session.query(User).filter(User.email == "testfarmer@hortisentry.org").first()
    assert fetched is not None
    assert fetched.id is not None
    assert fetched.role == "FARMER"
