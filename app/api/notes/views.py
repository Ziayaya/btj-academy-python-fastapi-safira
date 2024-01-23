from fastapi import APIRouter, Depends, Path, Request, Response, HTTPException
from api.base.base_schemas import PaginationParams
from middlewares.authentication import (
    get_user_id_from_access_token,
)

from .schemas import (
    NotesRequest,
    NotesResponse,
    ReadNotesResponse,
    ReadAllNotesRequest,
    ReadAllNotesResponse,
    UpdateNotesRequest,
    UpdateNotesResponse,
    DeleteNotesResponse
)
from .use_case import NewNotes, GetOneNote, ReadAllNotes, UpdateNote, DeleteNote

router = APIRouter(prefix="/notes")
tag = "Notes"


@router.post("/add", response_model=NotesResponse, tags=[tag])
async def create(
    request: Request,
    response: Response,
    data: NotesRequest,
    token_user_id: int = Depends(get_user_id_from_access_token),
    register: NewNotes = Depends(NewNotes),
) -> NotesResponse:
    """
    This API endpoint is for add notes.
    """
    try:
        # Execute the registration process
        resp_data = await register.execute(
            user_id=token_user_id,
            request=data,

        )

        # Return a successful response
        return NotesResponse(
            status="success",
            message="Successfully registered a new user",
            data=resp_data,
        )
    except HTTPException as ex:
        # Handle FastAPI HTTPExceptions
        response.status_code = ex.status_code
        return NotesResponse(
            status="error",
            message=ex.detail,
        )
    
    except Exception as e:
            # Handle other exceptions
            message = str(e)
            raise HTTPException(status_code=500, detail=message)
    

@router.get("/{note_id}", response_model=ReadNotesResponse, tags=[tag])
async def read_one_note(
    request: Request,
    response: Response,
    note_id: int = Path(..., description=""),
    token_user_id: int = Depends(get_user_id_from_access_token),
    read_note: GetOneNote = Depends(GetOneNote),
) -> ReadNotesResponse:
    """
    This API endpoint is for read one note.
    """
    try:
        resp_data = await read_note.execute(
            user_id=token_user_id,
            note_id=note_id
        )

        return ReadNotesResponse(
            status="success",
            message=f"success read note with id={note_id}",
            data=resp_data,
        )

    except HTTPException as ex:
        response.status_code = ex.status_code
        return ReadNotesResponse(
            status="error",
            message=ex.detail,
        )

    except Exception as e:
        # Handle other exceptions
        message = str(e)
        raise HTTPException(status_code=500, detail=message)

@router.get("", response_model=ReadAllNotesResponse, tags=[tag])
async def read_all(
    request: Request,
    response: Response,
    token_user_id: int = Depends(get_user_id_from_access_token),
    filter_user: bool = True,
    include_deleted: bool = False,
    page_params: PaginationParams = Depends(),
    read_all: ReadAllNotes = Depends(ReadAllNotes),
) -> ReadAllNotesResponse:
    """
    This API endpoint is for read all notes.
    """
    try:
        resp_data = await read_all.execute(
            user_id=token_user_id,
            page_params=page_params,
            filter_user=filter_user,
            include_deleted=include_deleted
        )

        return ReadAllNotesResponse(
            status="success",
            message="success read all notes",
            data=ReadAllNotesRequest(records=resp_data[0], meta=resp_data[1]),
        )

    except HTTPException as ex:
        response.status_code = ex.status_code
        return ReadAllNotesResponse(
            status="error",
            message=ex.detail,
        )

    except Exception as e:
        response.status_code = 500
        message = "failed to read all notes"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return ReadAllNotesResponse(
            status="error",
            message=message,
        )
    
@router.put("/{note_id}", response_model=UpdateNotesResponse, tags=[tag])
async def update_note(
    request: Request,
    response: Response,
    data: UpdateNotesRequest,
    note_id: int = Path(..., description=""),
    token_user_id: int = Depends(get_user_id_from_access_token),
    update_note: UpdateNote = Depends(UpdateNote),
) -> UpdateNotesResponse:
    """
    This API endpoint is for update existing note.
    """
    try:
        resp_data = await update_note.execute(
            user_id=token_user_id,
            note_id=note_id,
            request=data)

        return UpdateNotesResponse(
            status="success",
            message=f"success update note with id={note_id}",
            data=resp_data,
        )

    except HTTPException as ex:
        response.status_code = ex.status_code
        return UpdateNotesResponse(
            status="error",
            message=ex.detail,
        )

    except Exception as e:
        # Handle other exceptions
        message = str(e)
        raise HTTPException(status_code=500, detail=message)

@router.delete("/{note_id}", response_model=DeleteNotesResponse, tags=[tag])
async def delete_note(
    response: Response,
    request: Request,
    note_id: int = Path(..., description=""),
    token_user_id: int = Depends(get_user_id_from_access_token),
    delete_note: DeleteNote = Depends(DeleteNote),
) -> DeleteNotesResponse:
    """
    This API endpoint is for delete existing note.
    """
    try:
        resp_data = await delete_note.execute(
            user_id=token_user_id,
            note_id=note_id
        )

        return DeleteNotesResponse(
            status="success",
            message=f"success delete user with id={note_id}",
            data=resp_data,
        )

    except HTTPException as ex:
        response.status_code = ex.status_code
        return DeleteNotesResponse(
            status="error",
            message=ex.detail,
        )

    except Exception as e:
        # Handle other exceptions
        message = str(e)
        raise HTTPException(status_code=500, detail=message)
