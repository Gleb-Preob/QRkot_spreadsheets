from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_investment_goal,
                                check_project_before_deletion,
                                check_project_before_edit,
                                check_project_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import ProjectCreate, ProjectDB, ProjectUpdate

router = APIRouter()


@router.post(
    '/',
    response_model=ProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_project(
        project: ProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_project_name_duplicate(project.name, session)
    new_project = await charity_project_crud.create(project, session)
    # new_project = await charity_project_crud.free_funds_invest(
    #     new_project, session
    # )
    return new_project


@router.get(
    '/',
    response_model=list[ProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session)
):
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.patch(
    '/{project_id}',
    response_model=ProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_project(
        project_id: int,
        input_data: ProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await check_project_before_edit(
        project_id, session
    )
    if input_data.full_amount is not None:
        await check_investment_goal(
            project.invested_amount, input_data.full_amount
        )
    if input_data.name is not None:
        await check_project_name_duplicate(input_data.name, session)

    patched_project = await charity_project_crud.update(
        project, input_data, session
    )
    return patched_project


@router.delete(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await check_project_before_deletion(
        project_id, session
    )
    project = await charity_project_crud.remove(project, session)
    return project
