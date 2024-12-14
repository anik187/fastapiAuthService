from fastapi.requests import Request
from fastapi.responses import JSONResponse

from db.db import (SessionDep, create_user, get_user, update_password,
                   update_refreshToken)
from fastapi import APIRouter, HTTPException, status
from models.models import UpdatePassword, UserBase
from utils.hashPass import comparePassword, hashPassword
from utils.Response import ApiResponse
from utils.tokenGenerator import (decodeToken, generateAccessToken,
                                  generateRefreshToken)

router = APIRouter(prefix="/api/v1")


@router.post("/register")
async def registerUser(user: UserBase, session: SessionDep):
    if user.email and user.password:
        existedUser = get_user(session, user.email)
        if existedUser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User with email already exists",
            )
        refreshToken = generateRefreshToken(user.email)
        hashedPassword = hashPassword(user.password)
        createdUser = create_user(
            session, user.email, hashedPassword.decode("utf-8"), refreshToken
        )
        response = ApiResponse(
            status.HTTP_201_CREATED,
            {"email": createdUser.email},
            "successfully created user",
        )
        return JSONResponse(
            content=response,
            status_code=status.HTTP_201_CREATED,
            media_type="application/json",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="all fields are required"
        )


@router.post("/login")
async def loginUser(user: UserBase, session: SessionDep):
    if user.email and user.password:
        existedUser = get_user(session, user.email)
        if existedUser:
            isPasswordCorrect = comparePassword(
                userInput=user.password, hashedPassword=existedUser.password
            )
            if not isPasswordCorrect:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Password!!",
                )
            else:
                accessToken = generateAccessToken(existedUser.email)
                refreshToken = generateRefreshToken(existedUser.email)
                updatedUser = update_refreshToken(session, existedUser, refreshToken)
                response = JSONResponse(
                    content=ApiResponse(
                        status.HTTP_200_OK,
                        {"email": updatedUser.email},
                        "successfully loggedIn",
                    ),
                    status_code=status.HTTP_200_OK,
                    media_type="application/json",
                )
                response.set_cookie(
                    key="accessToken",
                    value=accessToken,
                    httponly=True,
                    secure=True,
                )
                response.set_cookie(
                    key="refreshToken",
                    value=refreshToken,
                    httponly=True,
                    secure=True,
                )
                return response
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enter email and password correctly!!!",
        )


@router.patch("/updatePassword")
async def updatePassword(
    request: Request, session: SessionDep, fixPassword: UpdatePassword
):

    if "accessToken" not in request.cookies or request.cookies["accessToken"] == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )
    accessToken = request.cookies["accessToken"]
    # refreshToken = request.cookies["refreshToken"]

    decodedToken = decodeToken(accessToken)
    oldPassword = fixPassword.oldPassword
    newPassword = fixPassword.newPassword

    if oldPassword != "" and newPassword != "":

        existedUser = get_user(session, decodedToken["email"])
        if existedUser:
            isPasswordCorrect = comparePassword(oldPassword, existedUser.password)
            if not isPasswordCorrect:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Old Password"
                )
            newPassword = hashPassword(plainPassword=newPassword)
            updatedUser = update_password(
                session, existedUser, newPassword.decode("utf-8")
            )
            response = ApiResponse(
                status_code=status.HTTP_200_OK,
                data={"email": updatedUser.email},
                message="Updated Password successfully!!",
            )
            return JSONResponse(
                content=response,
                media_type="application/json",
                status_code=status.HTTP_200_OK,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User!!"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="All fields are required!!!"
        )


@router.post("/logout")
async def logoutUser(request: Request, session: SessionDep):
    if "accessToken" not in request.cookies or request.cookies["accessToken"] == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )
    accessToken = request.cookies["accessToken"]
    decodedToken = decodeToken(accessToken)
    existedUser = get_user(session, decodedToken["email"])

    if existedUser:
        update_refreshToken(session, existedUser, "")
        response_prep = ApiResponse(
            status_code=status.HTTP_200_OK,
            data={},
            message="User LoggedOut successfully!!",
        )
        response = JSONResponse(
            content=response_prep,
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
        response.delete_cookie(key="accessToken", httponly=True, secure=True)
        response.delete_cookie(key="refreshToken", httponly=True, secure=True)
        return response

    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Problem!!",
        )
