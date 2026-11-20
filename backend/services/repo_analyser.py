from datetime import datetime, timezone


class RepoAnalyser:
    def __init__(self, repo):
        self.repo = repo

    def repository_age(self):
        created_at = self.repo.get("created_at")
        if created_at:
            created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - created_date).days
        return None

    def days_since_last_push(self):
        pushed_at = self.repo.get("pushed_at")
        if pushed_at:
            pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - pushed_date).days
        return None

    def activity_level(self):
        days_since_push = self.days_since_last_push()

        if days_since_push is None:
            return "Unknown"
        if days_since_push <= 7:
            return "Active"
        if days_since_push <= 30:
            return "Moderately Active"
        if days_since_push <= 90:
            return "Occasionally Active"
        if days_since_push <= 180:
            return "Stale"
        return "Inactive"

    def maintenance_assessment(self, commit_activity=None):
        commit_activity = commit_activity or {}
        days_since_push = self.days_since_last_push()
        pushed_at = self.repo.get("pushed_at")
        archived = self.repo.get("archived", False)

        if archived:
            return {
                "score": None,
                "max_score": 0,
                "grade": "Archived",
                "status": "Archived — excluded from maintenance scoring",
                "last_push_date": pushed_at,
                "days_since_last_push": days_since_push,
                "active_months": None,
                "commits_last_six_months": None,
                "history_capped": False,
                "reasons": ["Archived repositories are excluded from the maintenance score."]
            }

        if days_since_push is None:
            return {
                "score": None,
                "max_score": 0,
                "grade": "Unavailable",
                "status": "Push date unavailable",
                "last_push_date": None,
                "days_since_last_push": None,
                "active_months": None,
                "commits_last_six_months": None,
                "history_capped": False,
                "reasons": ["GitHub did not provide a last-push date, so this repository could not be scored."]
            }

        if days_since_push <= 7:
            recency_score = 5
            recency_reason = "Last pushed within the past week."
        elif days_since_push <= 30:
            recency_score = 4
            recency_reason = "Last pushed within the past month."
        elif days_since_push <= 90:
            recency_score = 3
            recency_reason = "Last pushed within the past three months."
        elif days_since_push <= 180:
            recency_score = 2
            recency_reason = "Last pushed within the past six months."
        elif days_since_push <= 365:
            recency_score = 1
            recency_reason = "Last pushed between six months and one year ago."
        else:
            recency_score = 0
            recency_reason = "No push has been recorded in over a year."

        history_available = commit_activity.get("available", False)
        reasons = [recency_reason]

        if history_available:
            active_months = commit_activity.get("active_months", 0)
            commit_count = commit_activity.get("commit_count", 0)

            if active_months >= 5:
                frequency_score = 5
            else:
                frequency_score = active_months

            reasons.append(
                f"Commits were found in {active_months} of the last 6 months "
                f"({commit_count} commits observed)."
            )
            if commit_activity.get("history_capped"):
                reasons.append(
                    "The commit history reached the 100-commit retrieval limit; "
                    "the commit count and active months may be underreported."
                )

            max_score = 10
            score = recency_score + frequency_score
        else:
            active_months = None
            commit_count = None
            frequency_score = None
            max_score = 5
            score = recency_score
            reasons.append(
                "Commit frequency could not be verified, so only push recency "
                "is included in this score."
            )

        if score >= 9:
            grade = "Excellent"
        elif score >= 7:
            grade = "Good"
        elif score >= 5:
            grade = "Fair"
        else:
            grade = "Needs work"

        return {
            "score": score,
            "max_score": max_score,
            "grade": grade,
            "status": self.activity_level(),
            "last_push_date": pushed_at,
            "days_since_last_push": days_since_push,
            "active_months": active_months,
            "commits_last_six_months": commit_count,
            "history_capped": commit_activity.get("history_capped", False),
            "recency_score": recency_score,
            "frequency_score": frequency_score,
            "reasons": reasons
        }
