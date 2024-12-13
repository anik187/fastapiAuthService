import os
from typing import Annotated

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

from fastapi import Depends

load_dotenv(dotenv_path=".env")

mysql_url = os.getenv("MYSQL_URL")
engine = create_engine(f"mysql{mysql_url}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
