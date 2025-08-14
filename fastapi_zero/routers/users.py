from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: T_Session,
    limit: int = 10,
    offset: int = 0,
):
    users = await session.scalars(
        select(User).limit(limit).offset(offset)
    )
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Sem permissão'
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Sem permissão'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'user delete'}


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username)
            | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                detail='Username ja existe',
                status_code=HTTPStatus.CONFLICT,
            )

        elif db_user.email == user.email:
            raise HTTPException(
                detail='Email ja existe',
                status_code=HTTPStatus.CONFLICT,
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def read_user_by_id(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,  # Adiciona autenticação
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Sem permissão'
        )

    user_db = await session.scalar(
        select(User).where(User.id == user_id)
    )
    if not user_db:
        raise HTTPException(
            detail='Não encontrado', status_code=HTTPStatus.NOT_FOUND
        )

    return user_db
