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
    repo_contents = fetcher.repo_contents()

    print(f"repos: {time.time() - start:.2f}s")


    # -----------------------------
    # Repository quality analysis
    # -----------------------------

    # -----------------------------
    # General GitHub analysis
    # -----------------------------

    

    print(f"analyser: {time.time() - start:.2f}s")


    # -----------------------------
    # Response
    # -----------------------------

    return {
        "events": events,
        "repos": repos,
        "repo_contents": repo_contents,
        "users": user_profile,
    }