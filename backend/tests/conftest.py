import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.main import app
from app.database.seed_data import seed_initial_data

# Use SQLite memory with StaticPool for test suite isolation across threads
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_initial_data(session)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def create_synthetic_image_bytes(format_name="JPEG", color=(100, 150, 80), size=(300, 300), add_sharp_pattern=True) -> bytes:
    """Helper to create synthetic test image bytes with Pillow."""
    img = Image.new("RGB", size, color=color)
    if add_sharp_pattern:
        draw = ImageDraw.Draw(img)
        for i in range(0, size[0], 20):
            draw.line([(i, 0), (i, size[1])], fill=(0, 0, 0), width=3)
            draw.line([(0, i), (size[0], i)], fill=(255, 255, 255), width=3)
    
    buf = pytest.importorskip("io").BytesIO()
    img.save(buf, format=format_name)
    return buf.getvalue()
