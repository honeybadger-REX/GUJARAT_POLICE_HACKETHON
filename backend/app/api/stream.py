from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_streams():
    return {
        "message": "Streams API"
    }