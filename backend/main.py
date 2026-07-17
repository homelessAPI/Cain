from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from activity.analysis import GitHubAnalyzer
from dataControl.models import User
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
    username = user.username
    print(f"Received username: {username}")
    url = f"https://api.github.com/users/{username}"
    events_url = f"https://api.github.com/users/{username}/events"
    repos_url = f"https://api.github.com/users/{username}/repos"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            events_response = requests.get(events_url, timeout=10)
            events_data = events_response.json()
            repos_response = requests.get(repos_url, timeout=10)

            if events_response.status_code != 200:
                raise HTTPException(
                    status_code=events_response.status_code,
                    detail="Failed to retrieve events.")
            elif events_data == []:
                raise HTTPException(
    status_code=404,
    detail=f"No events found for user '{username}'."
)
            else:
                events = []
                for i in events_data:
                    date = datetime.fromisoformat(i["created_at"].replace("Z", "+00:00"))
                    print("date: " + str(date))

                    events.append({
                    "type": i["type"],
                    "repository": i["repo"]["name"],
                    "repository_url": i["repo"]["url"],
                    "created_at": date,
                    "public": i["public"]
                })

                data = response.json()
                user = {
                    "profile": data["avatar_url"],
                    "following": data["following"],
                    "followers": data["followers"],
                    "public_repos": data["public_repos"],
                    "company": data["company"]
                    }
                
                analyser = GitHubAnalyzer(events_data)
               
                return {"events": events, "users": user, "Weekly_usage": analyser.weekday_counter()}

        else:
            raise HTTPException(
                status_code=404,
                detail="Failed to retrieve data for user."
)
    except requests.RequestException as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    return {"message": "Hello from backend!"}

if __name__ == "__main__":
    main()
