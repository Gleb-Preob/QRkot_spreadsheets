from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.crud.utils import close_entry
from app.models import CharityProject, Donation, User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


COMPLIMENTARY_MODELS = {
    CharityProject: Donation,
    Donation: CharityProject
}


class CRUDBase(
    Generic[ModelType, CreateSchemaType]
):

    def __init__(
        self,
        model: Type[ModelType]
    ):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ) -> List[ModelType]:
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        # ComplimentaryModel: Union[Type[CharityProject], Type[Donation]],
        user: Optional[User] = None
    ) -> ModelType:
        obj_in_data = obj_in.dict()
        # словарь для создания модели дополняется user.id
        if user is not None:
            obj_in_data['user_id'] = user.id
        new_db_obj = self.model(**obj_in_data)
        session.add(new_db_obj)
        await session.commit()
        await session.refresh(new_db_obj)

        ComplimentaryModel = COMPLIMENTARY_MODELS[self.model]
        open_comp_objects = await session.execute(
            select(ComplimentaryModel).where(
                ComplimentaryModel.fully_invested == False  # noqa: E712
            ).order_by(ComplimentaryModel.create_date)
        )
        open_comp_objects = open_comp_objects.scalars().all()

        for obj in open_comp_objects:
            delta_funds = (
                new_db_obj.full_amount - new_db_obj.invested_amount -
                (obj.full_amount - obj.invested_amount)
            )

            if delta_funds == 0:
                new_db_obj = await close_entry(new_db_obj)
                obj = await close_entry(obj)
            elif delta_funds < 0:
                new_db_obj = await close_entry(new_db_obj)
                obj.invested_amount = obj.full_amount + delta_funds
            elif delta_funds > 0:
                obj = await close_entry(obj)
                new_db_obj.invested_amount = (
                    new_db_obj.full_amount - delta_funds
                )

            session.add(new_db_obj)
            session.add(obj)

        await session.commit()
        await session.refresh(new_db_obj)
        return new_db_obj
