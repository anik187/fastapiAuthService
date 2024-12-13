from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str = Field(default=None, primary_key=True)
    password: str


class Users(UserBase, table=True):
    refreshToken: str


class updateUser(SQLModel):
    email: str | None = None
    password: str | None = None
    refreshToken: str | None = None

class UpdatePassword(SQLModel):
    oldPassword: str = ""
    newPassword: str = ""
