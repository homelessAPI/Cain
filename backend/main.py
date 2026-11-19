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

    profile_analyzer = GitHubAnalyzer(events, repos)
    weekly_usage = profile_analyzer.weekday_counter()
    languages = profile_analyzer.language_categorizer()

    if repos:
        quality_analyzer = RepositoryQualityAnalyzer(repos[0])

        (
            readme_quality,
            readme_scores,
            readme_reasons,
            total_readme_score
        ) = quality_analyzer.readme_quality(repo_contents)
    else:
        readme_quality = {}
        readme_scores = {}
        readme_reasons = {}
        total_readme_score = 0

    max_readme_score = len(repo_contents) * 5

    if max_readme_score:
        readme_percentage = round(
            total_readme_score / max_readme_score * 100,
            1
        )
    else:
        readme_percentage = 0

    print(f"analyser: {time.time() - start:.2f}s")

    return {
        "repos": repos,
        "repo_contents": repo_contents,
        "readme_quality": readme_quality,
        "readme_scores": readme_scores,
        "readme_reasons": readme_reasons,
        "total_readme_score": total_readme_score,
        "max_readme_score": max_readme_score,
        "readme_percentage": readme_percentage,
        "Weekly_usage": weekly_usage,
        "languages": languages,
        "users": user_profile,
    }
