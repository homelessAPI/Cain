from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.analyser import GitHubAnalyzer
from services.dataCompile import FetchData
from models.models import User
from Quality_Analyzer.repository_quality_analyzer import RepositoryQualityAnalyzer

import time


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cain-sable.vercel.app",
        "https://cain-git-main-spade2.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/")
def main(user: User):
    start = time.time()
    fetcher = FetchData(user.username)

    user_profile = fetcher.user_info()
    events = fetcher.events()
    repos = fetcher.repos()
    repo_contents = fetcher.repo_contents(repos)
    commit_activity = fetcher.repo_commit_activity(repos)

    profile_analyzer = GitHubAnalyzer(events, repos)
    weekly_usage = profile_analyzer.weekday_counter()
    languages = profile_analyzer.language_categorizer()

    if repos:
        quality_analyzer = RepositoryQualityAnalyzer(repos[0])

        (
            documentation_quality,
            documentation_scores,
            documentation_reasons,
            total_documentation_score
        ) = quality_analyzer.documentation_quality(repo_contents)

        maintenance = quality_analyzer.maintenance_quality(
            repos,
            commit_activity
        )
    else:
        documentation_quality = {}
        documentation_scores = {}
        documentation_reasons = {}
        total_documentation_score = 0
        maintenance = {
            "repositories": {},
            "total_score": 0,
            "max_score": 0,
            "percentage": 0
        }

    max_documentation_score = len(repo_contents) * 5
    documentation_percentage = (
        round(total_documentation_score / max_documentation_score * 100, 1)
        if max_documentation_score else 0
    )

    print(f"analyser: {time.time() - start:.2f}s")

    return {
        "repos": repos,
        "repo_contents": repo_contents,
        "documentation_quality": documentation_quality,
        "documentation_scores": documentation_scores,
        "documentation_reasons": documentation_reasons,
        "total_documentation_score": total_documentation_score,
        "max_documentation_score": max_documentation_score,
        "documentation_percentage": documentation_percentage,
        "maintenance": maintenance["repositories"],
        "maintenance_total_score": maintenance["total_score"],
        "maintenance_max_score": maintenance["max_score"],
        "maintenance_percentage": maintenance["percentage"],
        "Weekly_usage": weekly_usage,
        "languages": languages,
        "users": user_profile,
    }
