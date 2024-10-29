from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    Form,
    File,
    Depends,
    Request,
)
from fastapi.responses import FileResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import Upload, Uploaded_id
from app.models import User, Images
from pathlib import Path
import os
from app.api.login_register import oauth2_scheme, verify_token

router = APIRouter(prefix="/images",tags=['IMAGES'])

@router.post(
    "/profile",
    status_code=status.HTTP_201_CREATED,
    response_model=Upload,
    responses={
        400: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        }
    },
    # tags=['']
    dependencies=[Depends(oauth2_scheme)],
)
async def save_file(request: Request, upload_file: UploadFile = File(...), db:Session = Depends(get_db)):
    try:
        payload = verify_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token expired or invalid {e}",
        )
    user_email = payload["sub"]
    db_user = db.query(User).filter(User.email == user_email).first()
    if not user_email or not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or no user email found",
        )
    if upload_file.content_type not in [
        "image/jpg",
        "image/png",
        "image/gif",
        "image/jpeg",
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only JPEG, PNG, and GIF are allowed.",
        )
    save_directory = "images"

    os.makedirs(save_directory, exist_ok=True)

    file_location = os.path.join(save_directory, upload_file.filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await upload_file.read())
    image = Images(image_path=file_location)
    db.add(image)
    db.commit()
    db_user.user_img = image.id
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"message": "uploaded"}


@router.get("/{image_id}")
async def get_image(image_id: int, db:Session = Depends(get_db)):
    # Rasmni bazadan oling
    image = db.query(Images).filter(Images.id == image_id).first()
    print(image)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # Rasm fayl yo'lini tekshirish
    image_path = Path(image.image_path)  # `image_path` dan rasm yo'lini oling
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found on the server")

    return FileResponse(image_path)


@router.post(
    "/prod",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(oauth2_scheme)],
    response_model=Uploaded_id,
)
async def prod_img(upload_file: UploadFile = File(...), db:Session = Depends(get_db)):
    if upload_file.content_type not in [
        "image/jpg",
        "image/png",
        "image/gif",
        "image/jpeg",
    ]:
        raise HTTPException(
            status_code=400, detail="Invalid file format. Only jpeg,png and gif allowed"
        )
    save_directory = "images"
    os.makedirs(save_directory, exist_ok=True)
    file_location = os.path.join(save_directory, upload_file.filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await upload_file.read())
    image = Images(image_path=file_location)
    db.add(image)
    db.commit()
    db.refresh(image)
    db.close()
    return {"image_id": image.id}
