from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from src.app.config import get_settings
from src.app.logger_config import logger
from src.app.models.document import Base


class DataBase:
    def __init__(self, db_type: str, db_path: str):
        self._engine = self._create_engine(db_type, db_path)
        self.session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
        )
        Base.metadata.create_all(self._engine)
        logger.info(f"The database is configured and the tables are created.")

    def _create_engine(self, db_type: str, db_path: str) -> Engine:
        connection_string = f"{db_type}:///{db_path}"

        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"The path to the db: {db_dir.resolve() / Path(db_path).name}")

        engine = create_engine(
            connection_string, connect_args={"check_same_thread": False}
        )

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        return engine


settings = get_settings()

DB_FILE_PATH = f"{settings.data_dir}/sql_app.db"

db = DataBase(db_type="sqlite", db_path=DB_FILE_PATH)


def get_db():
    session = db.session_factory()
    try:
        yield session
    finally:
        session.close()
