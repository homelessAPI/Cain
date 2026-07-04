from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tabulate import tabulate
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.get("/")
def main(username: str):
    url = f"https://api.github.com/users/{username}"
    events_url = f"https://api.github.com/users/{username}/events"
    repos_url = f"https://api.github.com/users/{username}/repos"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            events_response = requests.get(events_url, timeout=10)

            if events_response.status_code != 200:
                raise HTTPException(f"Failed to retrieve events.", status_code=events_response.status_code)
            elif events_response.json() == []:
                raise HTTPException(f"No events found for user '{username}'.", status_code=404)
            else:
                rows = []
                for i in events_response.json():
                    rows.append([
                    i["type"],
                    i["repo"]["name"],
                    i["repo"]["url"],
                    i["created_at"],
                    i["public"]
                ])

                header = ["Event Type", "Repository", "Repository_URL", "Created At", "Public"]
                table = tabulate(rows, headers=header, tablefmt="grid")
                return {"table": table}

        else:
            raise HTTPException(f"Failed to retrieve data for user.", status_code={response.status_code})
    except Exception as e:
        raise HTTPException(f"An error occurred while making the API request: {e}")

    return {"message": "Hello from backend!"}

if __name__ == "__main__":
    main()
