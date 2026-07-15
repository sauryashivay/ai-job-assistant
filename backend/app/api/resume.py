from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.resume import ResumeProfile
from backend.app.services.resume_analyzer import analyze_resume
from backend.app.services.resume_parser import extract_resume_text

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post(
    "/analyze",
    response_model=ResumeProfile,
)
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
) -> ResumeProfile:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file has no filename.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume must be smaller than 5 MB.",
        )

    try:
        resume_text = extract_resume_text(
            filename=file.filename,
            file_bytes=file_bytes,
        )

        return analyze_resume(resume_text)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    finally:
        await file.close()