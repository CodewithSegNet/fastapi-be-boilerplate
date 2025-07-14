import os, requests, io, mimetypes, cv2, asyncio
from typing import List, Optional, Union
from secrets import token_hex
from fastapi import HTTPException, status, UploadFile
from pathlib import Path
from api.utils.settings import settings
from api.utils.minio_service import minio_service


# BASE_DIR = Path(__file__).resolve().parent.parent.parent


async def upload_file_to_current_dir(
    file: str,
    allowed_extensions: Optional[list],
    save_extension: str
):

    # BASE_DIR = Path(__file__).resolve().parent

    # Check against invalid extensions

    if hasattr(file, 'filename'):
        file_name = file.filename.lower()
    else:
        # If it's a file-like object created from bytes
        file_name = getattr(file, 'filename', 'unnamed_file')

    file_extension = file_name.split('.')[-1]
    name = file_name.split('.')[0]

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='File cannot be blank')

    if allowed_extensions:
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')

    new_filename = f'{name}-{token_hex(5)}.{save_extension}'
    SAVE_FILE_DIR = os.path.join(settings.TEMP_DIR, new_filename)
    with open(SAVE_FILE_DIR, 'wb') as f:
        if hasattr(file, 'read'):
            # If it's a file-like object (e.g., BytesIO)
            if asyncio.iscoroutinefunction(file.read):
                # If it's an async file
                content = await file.read()
            else:
                # If it's not an async file
                content = file.read()
        else:
            # If it's already bytes content
            content = file

        f.write(content)

    return SAVE_FILE_DIR


async def upload_to_temp_dir(
    file,
    allowed_extensions: Optional[list],
    max_file_size: int,
    save_extension: str
):
    """_summary_

    Args:
        file (_type_): _description_
        allowed_extensions (Optional[list]): _description_
        max_file_size (int): Maximum file size that can be uploaded in MB
        save_extension (str): _description_

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        str: Path to stored file
    """

    file_extension = file.filename.split('.')[-1]
    name = file.filename.split('.')[0]

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='File cannot be blank'
        )

    if allowed_extensions:
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid file format'
            )

    # Check file size
    file_size = len(file.file.read())
    if file_size > (max_file_size * (1024 * 1024)):
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {max_file_size} MB.",
        )

    # Reset file pointer after reading
    await file.seek(0)

    new_filename = f'{name}-{token_hex(5)}.{save_extension}'
    SAVE_FILE_DIR = os.path.join(settings.TEMP_DIR, new_filename)

    with open(SAVE_FILE_DIR, 'wb') as f:
        content = await file.read()
        f.write(content)

    return SAVE_FILE_DIR


async def upload_multiple_files_to_tmp_dir(
    files: List[UploadFile],
    allowed_extensions: Optional[list],
    max_file_size: int,
    save_extension: str
):
    file_locations = []

    for file in files:
        file_location = await upload_to_temp_dir(
            file=file,
            allowed_extensions=allowed_extensions,
            max_file_size=max_file_size,
            save_extension=save_extension
        )
        file_locations.append(file_location)

    return file_locations


def delete_file(file_path: str):

    if os.path.exists(file_path):
        os.remove(file_path)


async def contains_face(image_path):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)

    if image is None:
        raise HTTPException(
            status_code=404, detail=f"Image not found or unable to load.",)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        return True

    raise HTTPException(
        status_code=400, detail=f"Image does not contain a face.",)


async def upload_audio_file(file):
    file_extension = file.filename.split(".")[-1]
    audio_file = await upload_to_temp_dir(
        file, 
        allowed_extensions=[
            'mp3',
            'wav',
        ],
        save_extension=file_extension,
        max_file_size=50
    )

    # Upload video file to temporary stirage bucket
    audio_url = minio_service.upload_to_tmp_bucket(source_file=audio_file)
    delete_file(audio_file)

    return audio_file

async def upload_image_file(file):
    file_extension = file.filename.split(".")[-1]
    image_file = await upload_to_temp_dir(
        file, 
        allowed_extensions=[
            'jpg',
            'png',
            'jpeg',
            'jfif'
        ],
        save_extension=file_extension,
        max_file_size=20
    )

    # Upload video file to temporary stirage bucket
    image_url = minio_service.upload_to_tmp_bucket(source_file=image_file)
    delete_file(image_file)

    return image_url



def get_media_type_from_extension(file_extension):
    """
    Given a file extension (e.g., 'mp4', 'jpg', 'pdf'), return the corresponding media type (MIME type).
    """
    media_type, _ = mimetypes.guess_type(f"dummy.{file_extension}")
    return media_type


def get_bytes_data_from_url(url: str):
    '''This function gets bytes data for a medis from a url'''
    
    response = requests.get(url, stream=True)
    bytes_data = io.BytesIO(response.content)
    
    return bytes_data
