# init_db.py
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from loguru import logger
from etl.github_data.config.settings import Config
from etl.github_data.database.models import Base


def create_database(database_name, user, password, host, port):
    try:
        # Connect to the default database
        conn = psycopg2.connect(
            dbname=database_name, user=user, password=password, host=host, port=port
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute(
            f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database_name}'"
        )
        exists = cur.fetchone()
        if not exists:
            # Create database if it doesn't exist
            cur.execute(f"CREATE DATABASE {database_name}")
            logger.info(f"Database '{database_name}' created.")
        else:
            logger.info(f"Database '{database_name}' already exists.")

        # Close connection
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")


from sqlalchemy import text


def init_db():
    # Attempt to create the database if it doesn't exist
    create_database(
        Config.DB_NAME, Config.DB_USER, Config.DB_PASS, Config.DB_HOST, Config.DB_PORT
    )

    # Create an engine instance
    engine = create_engine(Config.DATABASE_URI)

    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    except Exception as e:
        logger.error(f"Error creating extension: {e}")

    # Create all tables in the database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized and all tables created")
    except OperationalError as e:
        logger.error(f"Error in initializing database: {e}")


if __name__ == "__main__":
    init_db()
