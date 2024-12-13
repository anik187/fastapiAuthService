# import time
# from datetime import datetime, timedelta, timezone

# import jwt

# token = jwt.encode(
#     {
#         "user": "anik",
#         "mail": "asif.anik@gmail.com",
#         "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=2 * 60),
#     },
#     key="test",
# )


# print(token)

# time.sleep(2 * 61)

# try:

#     decodedToken = jwt.decode(token, key="test", algorithms=["HS256"])
#     print("\n\n")
#     print(decodedToken)
# except jwt.ExpiredSignatureError:
#     print("Token expired")
from sqlmodel import Session, create_engine
from src.models.models import UserBase,Users,updateUser

engine = create_engine("mysql+pymysql://root:test-mysql@localhost:3306/fastapi")


with Session(engine) as session:
    existedUser = session.get(Users, "test@test.com")
    if existedUser:
        updatedData = updateUser(refreshToken="test123").model_dump(exclude_unset=True)
        existedUser.sqlmodel_update(updatedData)
        session.add(existedUser)
        session.commit()
        session.refresh(existedUser)
    print(existedUser)
