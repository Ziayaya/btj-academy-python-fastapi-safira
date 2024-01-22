from pydantic import BaseModel, Field
from api.base.base_schemas import BaseResponse, PaginationMetaResponse 
from models.notes import NotesSchema

class NotesRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=6, max_length=500)

class NotesResponse(BaseResponse):
    data: dict | None

class ReadNotesResponse(BaseResponse):
    data: dict | None

class ReadAllNotesRequest(BaseModel):
    records: list[NotesSchema]
    meta: PaginationMetaResponse

class ReadAllNotesResponse(BaseResponse):
    data: dict | None

class UpdateNotesRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=6, max_length=500)

class UpdateNotesResponse(BaseResponse):
    data: dict | None

class DeleteNotesResponse(BaseResponse):
    data: dict | None