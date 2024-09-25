import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from auth.auth import authenticate_user, create_access_token, user_dependency
from db.db import db_dependency
from schemas.user import UserLoginSchema, UserResponse

auth_router = APIRouter(prefix="/auth", tags=['auth'])
logger = logging.getLogger("my_app")


@auth_router.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = await authenticate_user(
        UserLoginSchema(email=form_data.username, password=form_data.password),
        db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@auth_router.get("/current_user",  response_model=UserResponse)
async def get_current_user(user: user_dependency):
    logger.debug(f"Retrieved user: {user}")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }
