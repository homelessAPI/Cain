from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests

route = APIRouter()

load_dotenv()  # Load environment variables from .env file

app_id = os.getenv("APP_ID")
app_key = os.getenv("APP_KEY")

Adzuna_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=10&what=python&content-type=application/json".format(APP_ID=app_id, APP_KEY=app_key)

@route.get("/leaderboard")
def leaderboard():
    Adzuna_data_fetch = requests.get(Adzuna_URL)

    Adzuna_data = Adzuna_data_fetch.json()

    print(f"Adzuna data fetched successfully: {Adzuna_data}" )
    return Adzuna_data