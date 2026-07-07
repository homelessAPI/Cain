from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dataControl.models import User
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "https://cain-ny53l4byc-spade2.vercel.app"
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

            if events_response.status_code != 200:
                raise HTTPException(
                    status_code=events_response.status_code,
                    detail="Failed to retrieve events.")
            elif events_response.json() == []:
                raise HTTPException(
    status_code=404,
    detail=f"No events found for user '{username}'."
)
            else:
                events = []
                for i in events_response.json():
                    events.append({
                    "type": i["type"],
                    "repository": i["repo"]["name"],
                    "repository_url": i["repo"]["url"],
                    "created_at": i["created_at"],
                    "public": i["public"]
                })

                header = ["Event Type", "Repository", "Repository_URL", "Created At", "Public"]
               
                return {"events": events}

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
