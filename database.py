from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # <- use sessionmaker

DATABASE_URL = 'postgresql://postgres:abc123@localhost:5432/pizza_delivery_db'

engine = create_engine(DATABASE_URL, echo=True)

# Correct way to create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
