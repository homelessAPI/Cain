from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.analyser import GitHubAnalyzer
from services.dataCompile import FetchData
from models.models import User
from routes.review import router as review_router
from routes.leaderboard import route as leaderboard_router
from Quality_Analyzer.repository_quality_analyzer import RepositoryQualityAnalyzer

import time


app = FastAPI()

app.include_router(review_router)
app.include_router(leaderboard_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cain-sable.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
def main(user: User):

    start = time.time()

    # -----------------------------
    # Fetch GitHub data
    # -----------------------------

    fetcher = FetchData(user.username)

    print(f"FetchData initialized: {time.time() - start:.2f}s")

    user_profile = fetcher.user_info()

    print(f"user profile: {time.time() - start:.2f}s")

    events = fetcher.events()

    print(f"events: {time.time() - start:.2f}s")

    repos = fetcher.repos()

    print(f"repos: {time.time() - start:.2f}s")


    # -----------------------------
    # Repository quality analysis
    # -----------------------------

    quality_analyzer = RepositoryQualityAnalyzer(
        user.username,
        repos
    )

    quality_analyzer.analyze()

    quality_score = quality_analyzer.overall_score()


    # -----------------------------
    # General GitHub analysis
    # -----------------------------

    analyser = GitHubAnalyzer(
        events,
        repos
    )

    print(f"analyser: {time.time() - start:.2f}s")


    # -----------------------------
    # Response
    # -----------------------------

    return {
        "events": events,
        "repos": repos,
        "users": user_profile,
        "Weekly_usage": analyser.weekday_counter(),
        "languages": analyser.language_categorizer(),
        "quality": quality_score
    }