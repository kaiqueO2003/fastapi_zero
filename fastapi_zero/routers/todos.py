# pylama: ignore=PLR0913,PLR0917
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import Todo, User
from fastapi_zero.schemas import TodoPublic, TodoSchema
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[Session, Depends(get_session)]
T_User = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(
    todo: TodoSchema,
    session: T_Session,
    user: T_User,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
