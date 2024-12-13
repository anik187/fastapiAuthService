from sqlalchemy.exc import NoResultFound

from db.db import SessionDep
from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from models.models import UpdatePassword, UserBase, Users, updateUser
from utils.hashPass import comparePassword, hashPassword
from utils.Response import ApiResponse
from utils.tokenGenerator import (decodeToken, generateAccessToken,
                                  generateRefreshToken)

router = APIRouter(prefix="/api/v1")


@router.post("/register")
async def registerUser(user: UserBase, session: SessionDep):
    if user.email and user.password:
        try:
            existedUser = session.get_one(Users, user.email)
            if existedUser:
                raise HTTPException(
                    status_code=409, detail="User with email already exists"
                )
        except NoResultFound:

            refreshToken = generateRefreshToken(user.email)
            hashedPassword = hashPassword(user.password)
            createdUser = Users(
                email=user.email,
                password=hashedPassword.decode("utf-8"),
                refreshToken=refreshToken,
            )
            session.add(createdUser)
            session.commit()
            response = ApiResponse(
                201, {"email": user.email}, "successfully created user"
            )
            return JSONResponse(
                content=response, status_code=201, media_type="application/json"
            )
    else:
        raise HTTPException(status_code=400, detail="all fields are required")


@router.post("/login")
async def loginUser(user: UserBase, session: SessionDep):
    if user.email and user.password:
        try:
            existedUser = session.get_one(Users, user.email)
            if existedUser:
                isPasswordCorrect = comparePassword(
                    userInput=user.password, hashedPassword=existedUser.password
                )
                if not isPasswordCorrect:
                    raise HTTPException(status_code=401, detail="Invalid Password!!")
                else:
                    accessToken = generateAccessToken(existedUser.email)
                    refreshToken = generateRefreshToken(existedUser.email)
                    updatedData = updateUser(refreshToken=refreshToken).model_dump(
                        exclude_unset=True
                    )
                    existedUser.sqlmodel_update(updatedData)
                    session.add(existedUser)
                    session.commit()
                    session.refresh(existedUser)
                    response = JSONResponse(
                        content=ApiResponse(
                            200, {"email": existedUser.email}, "successfully loggedIn"
                        ),
                        status_code=200,
                        media_type="application/json",
                    )
                    response.set_cookie(
                        key="accessToken", value=accessToken, httponly=True, secure=True
                    )
                    response.set_cookie(
                        key="refreshToken",
                        value=refreshToken,
                        httponly=True,
                        secure=True,
                    )
                    return response
        except NoResultFound:
            raise HTTPException(status_code=404, detail="User does not exist!!!")
    else:
        raise HTTPException(
            status_code=401, detail="Enter email and password correctly!!!"
        )


@router.patch("/updatePassword")
async def updatePassword(
    request: Request, session: SessionDep, fixPassword: UpdatePassword
):

    if "accessToken" not in request.cookies or request.cookies["accessToken"] == "":
        raise HTTPException(status_code=401, detail="Not Authorized")
    accessToken = request.cookies["accessToken"]
    # refreshToken = request.cookies["refreshToken"]

    decodedToken = decodeToken(accessToken)
    oldPassword = fixPassword.oldPassword
    newPassword = fixPassword.newPassword

    if oldPassword != "" and newPassword != "":

        try:
            existedUser = session.get_one(Users, decodedToken["email"])

            if existedUser:
                isPasswordCorrect = comparePassword(oldPassword, existedUser.password)
                if not isPasswordCorrect:
                    raise HTTPException(status_code=403, detail="Invalid Old Password")
                newPassword = hashPassword(plainPassword=newPassword)
                updatedPassword = updateUser(
                    password=newPassword.decode("utf-8")
                ).model_dump(exclude_unset=True)
                existedUser.sqlmodel_update(updatedPassword)
                session.add(existedUser)
                session.commit()
                session.refresh(existedUser)
                response = ApiResponse(
                    status_code=203,
                    data={"email": existedUser.email},
                    message="Updated Password successfully!!",
                )
                return JSONResponse(
                    content=response, media_type="application/json", status_code=203
                )

        except NoResultFound:
            raise HTTPException(status_code=401, detail="Invalid User!!")
    else:
        raise HTTPException(status_code=403, detail="All fields are required!!!")


@router.post("/logout")
async def logoutUser(request: Request, session: SessionDep):
    if "accessToken" not in request.cookies or request.cookies["accessToken"] == "":
        raise HTTPException(status_code=401, detail="Not Authorized")
    accessToken = request.cookies["accessToken"]
    decodedToken = decodeToken(accessToken)
    try:
        existedUser = session.get_one(Users, decodedToken["email"])

        if existedUser:
            updatedRefreshToken = updateUser(refreshToken="").model_dump(
                exclude_unset=True
            )

            existedUser.sqlmodel_update(updatedRefreshToken)
            session.add(existedUser)
            session.commit()
            session.refresh(existedUser)
            response_prep = ApiResponse(
                status_code=200,
                data={},
                message="User LoggedOut successfully!!",
            )
            response = JSONResponse(
                content=response_prep, media_type="application/json", status_code=200
            )
            response.delete_cookie(key="accessToken", httponly=True, secure=True)
            response.delete_cookie(key="refreshToken", httponly=True, secure=True)
            return response

    except NoResultFound:
        raise HTTPException(status_code=500, detail="Internal Server Problem!!")
