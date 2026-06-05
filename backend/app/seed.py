import app.models  # Registers SQLAlchemy models with Base.metadata.
from app.db.session import Base, engine


def run() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema created. No sample records were inserted.")


if __name__ == "__main__":
    run()
