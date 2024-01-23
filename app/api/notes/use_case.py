import datetime
import math
from typing import Annotated

from fastapi import Depends, HTTPException

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from db import get_session
from api.base.base_schemas import PaginationMetaResponse, PaginationParams
from models.notes import Notes, NotesSchema
from .schemas import (
    NotesRequest,
    UpdateNotesRequest,
)

AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]


class NewNotes:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id, request: NotesRequest) -> NotesSchema:
        async with self.async_session.begin() as session:
            notes = await session.execute(
                select(Notes).where(Notes.created_by == user_id)
            )
            notes = notes.scalars().first()


            notes = Notes()
            notes.title = request.title
            notes.content = request.content
            notes.created_at = datetime.datetime.utcnow()
            notes.updated_at = datetime.datetime.utcnow()
            notes.created_by = user_id
            notes.updated_by = user_id

            session.add(notes)
            await session.flush()

            return NotesSchema.from_orm(notes)
        
class GetOneNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id, note_id) -> NotesSchema:
        async with self.async_session.begin() as session:
            notes = await session.execute(
                select(Notes).where(
                    (Notes.note_id == note_id).__and__(Notes.created_by == user_id).__and__(Notes.deleted_at == None)
                    )
            )
            notes = notes.scalars().first()

            if not notes:
                raise HTTPException(status_code=404)

            return NotesSchema.from_orm(notes)

class ReadAllNotes:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
            self, user_id: int, page_params: PaginationParams, filter_user: bool, include_deleted: bool
            ) -> (list[NotesSchema], PaginationMetaResponse):
        async with self.async_session() as session:
            total_item = (
                select(func.count())
                .select_from(Notes)
            )

            query = (
                select(Notes)
                .offset((page_params.page - 1) * page_params.item_per_page)
                .limit(page_params.item_per_page)
            )

            if filter_user:
                total_item = total_item.filter(Notes.created_by == user_id)
                query = query.filter(Notes.created_by == user_id)

            if not include_deleted:
                total_item = total_item.filter(Notes.deleted_at == None)
                query = query.filter(Notes.deleted_at == None)

            total_item = await session.execute(total_item)
            total_item = total_item.scalar()

            paginated_query = await session.execute(query)
            paginated_query = paginated_query.scalars().all()

            notes = [NotesSchema.from_orm(p) for p in paginated_query]

            meta = PaginationMetaResponse(
                total_item=total_item,
                page=page_params.page,
                item_per_page=page_params.item_per_page,
                total_page=math.ceil(total_item / page_params.item_per_page),
            )

            return notes, meta
        
class UpdateNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int, note_id: int, request: UpdateNotesRequest) -> NotesSchema:
        async with self.async_session.begin() as session:
            notes = await session.execute(
                select(Notes).where(
                    (Notes.note_id == note_id) & (Notes.created_by == user_id) & (Notes.deleted_at == None))
            )
            notes = notes.scalars().first()
            if not notes:
                raise HTTPException(status_code=404)
            

            notes.title = request.title
            notes.content = request.content
            notes.updated_at = datetime.datetime.utcnow()
            notes.updated_by = user_id

            await session.flush()

            return NotesSchema.from_orm(notes)

class DeleteNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session
    async def execute(self, user_id, note_id) -> NotesSchema:
        async with self.async_session.begin() as session:
            notes = await session.execute(
                select(Notes).where(
                    (Notes.note_id == note_id) & (Notes.created_by == user_id) & (Notes.deleted_at == None))
            )
            notes = notes.scalars().first()
            if not notes:
                raise HTTPException(status_code=404)
            
            notes.deleted_at = datetime.datetime.utcnow()
            notes.deleted_by = user_id

            await session.flush()

            return NotesSchema.from_orm(notes)
    