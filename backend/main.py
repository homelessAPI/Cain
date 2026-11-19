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
    repo_contents = fetcher.repo_contents()

    if repos:
        quality_analyzer = RepositoryQualityAnalyzer(repos[0])
        readme_quality, readme_scores = quality_analyzer.readme_quality(repo_contents)
    else:
        readme_quality = {}
        readme_scores = {}

    print(f"analyser: {time.time() - start:.2f}s")

    return {
        "events": events,
        "repos": repos,
        "repo_contents": repo_contents,
        "readme_quality": readme_quality,
        "readme_scores": readme_scores,
        "users": user_profile,
    }
