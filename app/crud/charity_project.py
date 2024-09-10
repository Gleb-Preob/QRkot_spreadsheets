from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.crud.utils import close_entry
from app.models import CharityProject
from app.schemas.charity_project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[
    CharityProject,
    ProjectCreate
]):
    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def update(
        self,
        project: CharityProject,
        obj_in: ProjectUpdate,
        session: AsyncSession,
    ) -> CharityProject:
        obj_data = jsonable_encoder(project)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(project, field, update_data[field])
        if project.full_amount - project.invested_amount == 0:
            project = await close_entry(project)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    async def remove(
        self,
        project: CharityProject,
        session: AsyncSession,
    ) -> CharityProject:
        await session.delete(project)
        await session.commit()
        return project

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession
    ):
        project_query = await session.execute(select(CharityProject).where(
            CharityProject.fully_invested == True  # noqa: E712
        ).order_by(
            (extract('year', CharityProject.close_date) - extract('year', CharityProject.create_date)).asc(),  # noqa: E501
            (extract('month', CharityProject.close_date) - extract('month', CharityProject.create_date)).asc(),  # noqa: E501
            (extract('day', CharityProject.close_date) - extract('day', CharityProject.create_date)).asc(),  # noqa: E501
            (extract('hour', CharityProject.close_date) - extract('hour', CharityProject.create_date)).asc(),  # noqa: E501
            (extract('minute', CharityProject.close_date) - extract('minute', CharityProject.create_date)).asc(),  # noqa: E501
            (extract('second', CharityProject.close_date) - extract('second', CharityProject.create_date)).asc(),  # noqa: E501
        ))
        return project_query.scalars().all()


charity_project_crud = CRUDProject(CharityProject)
