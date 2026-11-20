from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from requests import RequestException

from services.analyser import GitHubAnalyzer
from services.dataCompile import FetchData
from models.models import User
from Quality_Analyzer.repository_quality_analyzer import RepositoryQualityAnalyzer

import time


app = FastAPI()


@app.exception_handler(RequestException)
async def github_connection_error(request: Request, exc: RequestException):
    return JSONResponse(
        status_code=503,
        content={
            "detail": {
                "code": "GITHUB_CONNECTION_FAILED",
                "message": (
                    "Cain could not connect to GitHub. "
                    "GitHub may be temporarily unavailable; please try again."
                )
            }
        }
    )


@app.exception_handler(Exception)
async def cain_internal_error(request: Request, exc: Exception):
    print(f"Cain internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "CAIN_INTERNAL_ERROR",
                "message": (
                    "Cain ran into an internal problem while analyzing this profile. "
                    "Please try again later."
                )
            }
        }
    )


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
    pinned_repositories = fetcher.pinned_repositories()
    repo_trees = fetcher.repo_trees(repos, pinned_repositories)
    pull_requests = fetcher.pull_request_activity()

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
        project_hygiene = quality_analyzer.project_hygiene_quality(repos, repo_trees)
        profile_level = quality_analyzer.profile_level_assessment(
            user_profile, repos, events, pull_requests, pinned_repositories,
            documentation_scores, project_hygiene
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
        project_hygiene = {
            "repositories": {}, "total_score": 0, "max_score": 0,
            "percentage": 0, "scanned_count": 0, "total_count": 0
        }
        profile_level = {
            "internal_percentage": 0, "level": "Insufficient data",
            "strengths": [],
            "improvements": ["No repositories were available to assess this profile."]
        }

    max_documentation_score = len(repo_contents) * 5
    documentation_percentage = (
        round(total_documentation_score / max_documentation_score * 100, 1)
        if max_documentation_score else 0
    )

    assessment_scores = [
        documentation_percentage,
        maintenance["percentage"],
        project_hygiene["percentage"],
        profile_level["internal_percentage"]
    ]
    overall_percentage = round(sum(assessment_scores) / 4, 1)
    overall_grade = "A" if overall_percentage >= 85 else "B" if overall_percentage >= 70 else "C"

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
        "project_hygiene": project_hygiene["repositories"],
        "project_hygiene_total_score": project_hygiene["total_score"],
        "project_hygiene_max_score": project_hygiene["max_score"],
        "project_hygiene_percentage": project_hygiene["percentage"],
        "project_hygiene_scanned_count": project_hygiene["scanned_count"],
        "project_hygiene_total_count": project_hygiene["total_count"],
        "profile_level": profile_level,
        "overall_percentage": overall_percentage,
        "overall_grade": overall_grade,
        "Weekly_usage": weekly_usage,
        "languages": languages,
        "users": user_profile,
    }
