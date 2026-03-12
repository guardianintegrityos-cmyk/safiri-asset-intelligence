try:
    from sqlalchemy import create_engine  # type: ignore
    from sqlalchemy.ext.declarative import declarative_base  # type: ignore
    from sqlalchemy.orm import sessionmaker  # type: ignore
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

    # Fallback classes for when SQLAlchemy is not available
    class create_engine:
        def __init__(self, url):
            self.url = url

    class declarative_base:
        def __init__(self):
            pass

    class sessionmaker:
        def __init__(self, autocommit=False, autoflush=False, bind=None):
            self.autocommit = autocommit
            self.autoflush = autoflush
            self.bind = bind

        def __call__(self):
            return MockSession()

    class MockSession:
        def close(self):
            pass

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/safiri")

if SQLALCHEMY_AVAILABLE:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    engine = None
    SessionLocal = None
    Base = declarative_base()

def get_db():
    if not SQLALCHEMY_AVAILABLE:
        # Return a mock generator when SQLAlchemy is not available
        yield MockSession()
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()