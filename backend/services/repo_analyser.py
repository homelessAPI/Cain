from datetime import datetime, timezone
from services.dataCompile import FetchData

class RepoAnalyser:
    def __init__(self, repo):
        self.repo = repo
        self.fetcher = FetchData(repo.get("owner", {}).get("login", ""))
    
    def repository_age(self):
        created_at = self.repo.get("created_at")
        if created_at:
            created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_in_days = (datetime.now(timezone.utc) - created_date).days
            return age_in_days
        return None

    def days_since_last_push(self):
        
        pushed_at = self.repo.get("pushed_at")
        if pushed_at:
            pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_since_push = (datetime.now(timezone.utc) - pushed_date).days
            return days_since_push
        return None


    def activity_level(self):
        activity_level = "Unknown"
        days_since_push = self.days_since_last_push()

        if days_since_push is None:
            activity_level = "Unknown"
        elif days_since_push < 7:
            activity_level = "Active"
        elif days_since_push < 21:
            activity_level = "Moderately Active"
        elif days_since_push < 60:
            activity_level = "Stale"
        else:
            activity_level = "Inactive"
        return activity_level

    

if __name__ == "__main__":
    repo = {
        "Repo_name": "Test Project",
        "pushed_at": "2026-08-10T12:00:00Z"
    }

    analyser = RepoAnalyser(repo)
    analyser.days_since_last_push()
    analyser.activity_level()