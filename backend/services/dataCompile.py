from fastapi import HTTPException
from datetime import datetime
import requests

class FetchData:
    # Intalizations
    def __init__(self, username: str):
        self.username = username
        self.url = f"https://api.github.com/users/{username}"
        self.events_url = f"https://api.github.com/users/{username}/events"
        self.repos_url = f"https://api.github.com/users/{username}/repos"

        self.url_response = requests.get(self.url)
        self.events_response = requests.get(self.events_url)


        self.url_data = self.url_response.json()
        self.events_data = self.events_response.json()
        self.repos_data = self.fetch_repos()

        self.user_data = {}
        self.events_list = []
        self.repos_list = []

    def user_info(self):
        
        if self.url_response.status_code != 200:
            raise HTTPException(status_code=self.url_response.status_code, detail="Faild to fetch user data")
        elif self.url_response.status_code == []:
            raise HTTPException(status_code=self.url_response.status_code, detail="User profile is empty")
        elif self.url_response.status_code == 200:
            self.user_data  = {
                    "profile": self.url_data["avatar_url"],
                    "following": self.url_data["following"],
                    "followers": self.url_data["followers"],
                    "public_repos": self.url_data["public_repos"],
                    "company": self.url_data["company"],
                    "hireable": self.url_data["hireable"],
                    "bio": self.url_data["bio"]
                    }
            
            return self.user_data 

    # Method to fetch, process and return data from the events url
    def events(self):

        if self.events_response.status_code != 200:
            raise HTTPException(status_code=self.events_response.status_code, detail="Failed to retrive event data")
        
        elif self.events_data == []:
            raise HTTPException(status_code=self.events_response.status_code, detail="No event data found.")

        elif self.events_response.status_code == 200:

            for i in self.events_data:
                date = datetime.fromisoformat(i["created_at"].replace("Z", "+00:00"))

                self.events_list.append({
                    "type": i["type"],
                    "repository": i["repo"]["name"],
                    "repository_url": f"https://github.com/{i['repo']['name']}",
                    "created_at": date,
                    "public": i["public"]
            })
        #print("Url: " + str(self.url_data) + "\n\n")
        #print("event: " + str(self.events_data) + "\n\n")
        #print("Repos: " + str(self.repos_data) + "\n\n")
        return self.events_list
        
    # Method to fetch, process and retuan data from the repos url
    def fetch_repos(self):
        page = 1
        all_repos = []

        while True:
            repos_response = requests.get(self.repos_url, 
                                           params={"page": page, 
                                                   "per_page": 100})
            if repos_response.status_code != 200:
                raise HTTPException(status_code=repos_response.status_code, detail="Failed to retrieve repo data")
            elif repos_response.json() == []:
                break
            all_repos.extend(repos_response.json())
            page += 1

        return all_repos


    def repos(self):
        
        for j in self.repos_data:
            self.repos_list.append({
                "Repo_name": j["name"],
                "description": j['description'],
                "Private": j['private'],
                "created_at": j['created_at'],
                "updated_at": j['updated_at'],
                "forks": j['forks'],
                "stargazers_count": j['stargazers_count'],
                "watchers_count": j['watchers_count'],
                "size": j['size'],
                "default_branch": j['default_branch'],
                "open_issues_count": j['open_issues_count'],
                "pushed_at": j['pushed_at'],
                "owner": j['owner']['login'],
                "language": j['language'],
                "repo_url": j['html_url']
            })

        return self.repos_list

