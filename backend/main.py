from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.analyser import GitHubAnalyzer
from services.dataCompile import FetchData
from models.models import User
from datetime import datetime
import requests

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

    # Initalizations
    fetcher = FetchData(user.username)
    event = fetcher.events()
    repos = fetcher.repos()
    analyser = GitHubAnalyzer(event)

    # Error handling
    print("user info: " + str(fetcher.user_info) + "\n\n")
    # print("event: " + str(event) + "\n\n")
    # print("analyser: " + str(analyser.weekday_counter()) + "\n\n")

    return {"events": event, "repos": repos, "users": fetcher.user_info(), "Weekly_usage": analyser.weekday_counter()}

if __name__ == "__main__":
    main()
