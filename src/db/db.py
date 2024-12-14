import os
from typing import Annotated

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

from fastapi import Depends
from models.models import Users, updateUser

load_dotenv(dotenv_path=".env")

mysql_url = os.getenv("MYSQL_URL")
engine = create_engine(f"mysql{mysql_url}")


def get_session():
    with Session(engine) as session:
        yield session


def get_user(session: Session, email: str) -> Users | None:
    user = session.get(Users, email)
    return user


def create_user(
    session: Session, email: str, password: str, refreshToken: str
) -> Users:
    user = Users(email=email, password=password, refreshToken=refreshToken)
    session.add(user)
    session.commit()
    return user


def update_password(
    session: Session,
    existedUser: Users,
    newPassword: str,
) -> Users:
    updatedUser = updateUser(password=newPassword).model_dump(exclude_unset=True)
    existedUser.sqlmodel_update(updatedUser)
    session.add(existedUser)
    session.commit()
    session.refresh(existedUser)
    return existedUser


def update_refreshToken(
    session: Session,
    existedUser: Users,
    newRefreshToken: str,
) -> Users:
    updatedUser = updateUser(refreshToken=newRefreshToken).model_dump(
        exclude_unset=True
    )
    existedUser.sqlmodel_update(updatedUser)
    session.add(existedUser)
    session.commit()
    session.refresh(existedUser)
    return existedUser


SessionDep = Annotated[Session, Depends(get_session)]
