from http import HTTPStatus as Codes

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_project_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=Codes.BAD_REQUEST,
            detail='Проект с таким именем уже существует',
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=Codes.NOT_FOUND,
            detail='Проект не найден'
        )
    return project


async def check_project_before_edit(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(
        project_id, session
    )
    if not project:
        raise HTTPException(
            status_code=Codes.NOT_FOUND, detail='Проект не найден'
        )
    if project.fully_invested is True:
        raise HTTPException(
            status_code=Codes.BAD_REQUEST,
            detail='Проект был выполнен, более не доступен для редактирования'
        )
    return project


async def check_project_before_deletion(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    project = await charity_project_crud.get(
        project_id, session
    )
    if not project:
        raise HTTPException(
            status_code=Codes.NOT_FOUND, detail='Проект не найден'
        )
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=Codes.BAD_REQUEST,
            detail='Проект получил финансирование и не может быть удалён'
        )

    return project


async def check_investment_goal(
        invested_amount: int,
        input_full_amount: int
) -> None:
    if invested_amount > input_full_amount:
        raise HTTPException(
            status_code=Codes.BAD_REQUEST,
            detail='Невозможно выставить целевую сумму меньше инвестированной'
        )
