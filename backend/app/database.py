from sqlmodel import SQLModel, create_engine, Session
import os

from pathlib import Path

default_data_dir = Path(__file__).parent.parent.parent / "data"
data_dir = os.getenv("DATA_DIR", str(default_data_dir))
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

sqlite_file_name = os.path.join(data_dir, "discvault.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
