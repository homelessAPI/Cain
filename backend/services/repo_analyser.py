from datetime import datetime, timezone
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
        if days_since_push is not None:
            if days_since_push < 7:
                activity_level = "Active"
            elif 7 <= days_since_push < 21:
                activity_level = "Moderately Active"
            elif 60 <= days_since_push < 365:
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

    def repo_content(self, owner, repo_name):
        url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Contents of the repository :" + str(response.json()))
            return response.json()
        else:
            return None
    

if __name__ == "__main__":
    repo = {
        "Repo_name": "Test Project",
        "pushed_at": "2026-08-10T12:00:00Z"
    }

    analyser = RepoAnalyser(repo)
    analyser.days_since_pushed()
    analyser.repo_content("homelessapi", "Abel")
    analyser.activity_level()