from datetime import datetime, timezone
from services.dataCompile import FetchData
import requests

class RepoAnalyser:
    def __init__(self, repo):
        self.repo = repo

    def days_since_pushed(self):
        
        pushed_at = self.repo.get("pushed_at")
        if pushed_at:
            pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_since_push = (datetime.now(timezone.utc) - pushed_date).days
            return days_since_push
        return None

    def activity_level(self):
        activity_level = "Unknown"
        days_since_push = self.days_since_pushed()
        if days_since_push < 7:
            activity_level = "Active"
        elif days_since_push < 21:
            activity_level = "Moderately Active"
        elif days_since_push < 60:
            activity_level = "Stale"
        else:
            activity_level = "Inactive"
        return activity_level

    def repository_age(self):
        created_at = self.repo.get("created_at")
        if created_at:
            created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_in_days = (datetime.now(timezone.utc) - created_date).days
            return age_in_days
        return None

    def is_fork(self):
        return self.repo.get("fork", False)

    def repo_content_review(self, owner, repo_name):
        fetcher = FetchData(owner)
        contents = fetcher.repo_contents(owner, repo_name)

        repo_content = {
                    "README.md": False,
                    "gitignore": False,
                    "LICENSE": False,
                    "Tests": False,
                    "Dockerfile": False
                }

        for content in contents:
                if content["name"] == "README.md":
                    repo_content["README.md"] = True
                elif content["name"] == ".gitignore":
                    repo_content["gitignore"] = True
                elif content["name"] == "LICENSE":
                    repo_content["LICENSE"] = True
                elif content["name"] == "Tests":
                    repo_content["Tests"] = True
                elif content["name"] == "Dockerfile":
                    repo_content["Dockerfile"] = True
        return repo_content
 

if __name__ == "__main__":
    repo = {
        "Repo_name": "Test Project",
        "pushed_at": "2026-08-10T12:00:00Z"
    }

    analyser = RepoAnalyser(repo)
    analyser.days_since_pushed()
    analyser.activity_level()