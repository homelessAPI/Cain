from fastapi import APIRouter
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

    review = ai.ask(prompt)

    return {
        "AI_Review": review
    }