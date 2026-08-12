

class RepoAnalyser:
    def __init__(self, repo):
        self.repo = repo

    def days_since_pushed(self):
        from datetime import datetime
        pushed_at = self.repo.get("pushed_at")
        if pushed_at:
            pushed_date = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
            days_since_push = (datetime.utcnow() - pushed_date).days
            print(f"Days since last push for {self.repo.get('Repo_name')}: {days_since_push} days")
            return days_since_push
        return None

    def activity_level(self):
        activity_level = "Unknown"
        days_since_push = self.days_since_pushed()
        if days_since_push is not None:
            if days_since_push < 5:
                activity_level = "Active"
            elif 5 <= days_since_push < 20:
                activity_level = "Moderately Active"
            elif 20 <= days_since_push < 90:
                activity_level = "Stale"
            else:
                activity_level = "Inactive"
        print(f"Activity level for {self.repo.get('Repo_name')}: {activity_level}")
        return activity_level

repo = {
    "Repo_name": "Test Project",
    "pushed_at": "2026-08-10T12:00:00Z"
}

analyser = RepoAnalyser(repo)
analyser.days_since_pushed()

analyser.activity_level()