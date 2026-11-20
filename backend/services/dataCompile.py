from fastapi import HTTPException
from datetime import datetime
import requests
import base64


class FetchData:

    def __init__(self, username: str):
        self.username = username

        self.url = f"https://api.github.com/users/{username}"
        self.events_url = f"https://api.github.com/users/{username}/events"
        self.repos_url = f"https://api.github.com/users/{username}/repos"

    # -------------------------
    # USER
    # -------------------------

    def fetch_user_info(self):
        response = requests.get(self.url)
        #print(f"user_info: {self.url}")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch user data"
            )

        data = response.json()
        #print(f"User info data: {data}")

        if not data:
            raise HTTPException(
                status_code=404,
                detail="User profile is empty"
            )

        return data

    def user_info(self):
        data = self.fetch_user_info()

        return {
            "profile": data["avatar_url"],
            "following": data["following"],
            "followers": data["followers"],
            "public_repos": data["public_repos"],
            "company": data["company"],
            "hireable": data["hireable"],
            "bio": data["bio"]
        }

    # -------------------------
    # EVENTS
    # -------------------------

    def fetch_events_info(self):
        response = requests.get(self.events_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to retrieve event data"
            )

        data = response.json()

        return data

    def events(self):
        events_data = self.fetch_events_info()

        if not events_data:
            return []

        events_list = []

        for event in events_data:
            created_at = datetime.fromisoformat(
                event["created_at"].replace("Z", "+00:00")
            )

            events_list.append({
                "type": event["type"],
                "repository": event["repo"]["name"],
                "repository_url": f"https://github.com/{event['repo']['name']}",
                "created_at": created_at,
                "public": event["public"]
            })

        return events_list

    # -------------------------
    # REPOSITORIES
    # -------------------------

    def fetch_repos(self):
        page = 1
        all_repos = []

        while True:
            response = requests.get(
                self.repos_url,
                params={
                    "page": page,
                    "per_page": 100
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve repo data"
                )

            data = response.json()

            if not data:
                break

            all_repos.extend(data)
            page += 1

        return all_repos
    
    def fetch_repo_contents(self, repo_name):
        branch = "main"  
        repo_contents_url = f"https://api.github.com/repos/{self.username}/{repo_name}/git/trees/{branch}?recursive=1"

        response = requests.get(
            repo_contents_url.format(repo_name=repo_name)
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to retrieve contents for repo: {repo_name}"
            )

        data = response.json()

        return data
    
    def repos(self):
        repos_data = self.fetch_repos()
        repos_list = []

        for repo in repos_data:
            repos_list.append({
                "Repo_name": repo["name"],
                "description": repo["description"],
                "Private": repo["private"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "forks": repo["forks"],
                "stargazers_count": repo["stargazers_count"],
                "watchers_count": repo["watchers_count"],
                "size": repo["size"],
                "default_branch": repo["default_branch"],
                "open_issues_count": repo["open_issues_count"],
                "pushed_at": repo["pushed_at"],
                "owner": repo["owner"]["login"],
                "language": repo["language"],
                "repo_url": repo["html_url"]
            })

            
        return repos_list

    # -------------------------
    # REPOSITORY CONTENTS
    # -------------------------

    def repo_contents(self, repos_list=None):

        repos_contents = self.fetch_repos() if repos_list is None else repos_list
        print(f"repos_contents: {repos_contents}")

        if repos_list is None:
            repos_list = self.repos()
        Readme_dict = {}
        Readme_Content = {}

        for repo in repos_list:
            readme_url = f"https://api.github.com/repos/{self.username}/{repo['Repo_name']}/readme"
            readme_response = requests.get(readme_url)
            Readme_dict[repo["Repo_name"]] = readme_response.json()

        for repo_name, readme_data in Readme_dict.items():
            if "content" in readme_data:
                content = readme_data["content"]
                decoded_content = base64.b64decode(content).decode("utf-8")
                Readme_Content[repo_name] = decoded_content
                Readme_dict[repo_name]["decoded_content"] = decoded_content
            else:
                Readme_dict[repo_name]["decoded_content"] = None
                Readme_Content[repo_name] = None

        #print(f"Readme_Content: {Readme_Content}")

        return Readme_Content

    