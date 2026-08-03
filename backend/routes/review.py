from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.models import User
from prompts.review_prompt import build_review_prompt
from services.ai_service import AIReviwer
from services.dataCompile import FetchData

router = APIRouter()

ai = AIReviwer()


@router.post("/review")
def review(user: User):

    fetcher = FetchData(user.username)

    user_profile = fetcher.user_info()
    events = fetcher.events()
    repos = fetcher.repos()

    prompt = build_review_prompt(
        user_profile,
        repos[:5],
        events[:5]
    )

    return StreamingResponse(
        ai.ask_stream(prompt),
        media_type="text/plain"
    )