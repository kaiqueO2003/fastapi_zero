from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Token
from fastapi_zero.security import (
    create_acess_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix=('/auth'), tags=['auth'])
T_Session = Annotated[Session, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_acess_token(
    session: T_Session,
    form_data: T_OAuth2Form,
):
    user = session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not User or not verify_password(
        form_data.password, user.password
    ):
        raise HTTPException(
            status_code=400, detail='incorreto email ou senha'
        )

    acess_token = create_acess_token(data={'sub': user.email})

    return {'acess_token': acess_token, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=Token)
def refresh_acess_token(
    user: User = Depends(get_current_user),
):
    new_acess_token = create_acess_token(data={'sub': user.email})

    return {'acess_token': new_acess_token, 'token_type': 'Bearer'}
