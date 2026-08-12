from datetime import datetime, timezone

class RepoAnalyser:
    def __init__(self, repo):
        self.repo = repo

    def days_since_pushed(self):
        
        pushed_at = self.repo.get("pushed_at")
        if pushed_at:
            pushed_date = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
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


if __name__ == "__main__":
    repo = {
        "Repo_name": "Test Project",
        "pushed_at": "2026-08-10T12:00:00Z"
    }

    analyser = RepoAnalyser(repo)
    analyser.days_since_pushed()

    analyser.activity_level()