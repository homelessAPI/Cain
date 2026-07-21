from datetime import datetime
from collections import Counter

class GitHubAnalyzer:

    def __init__(self, events, repos):
        self.events = events
        self.repos = repos

    def weekday_counter(self):

        try:
            weekday_count = {
                "Monday": 0,
                "Tuesday": 0,
                "Wednesday": 0,
                "Thursday": 0,
                "Friday": 0,
                "Saturday": 0,
                "Sunday": 0
            }

            for event in self.events:
                date = event["created_at"]

                weekday = date.strftime("%A")

                weekday_count[weekday] += 1

            return weekday_count
        except Exception as e:
            return {"message": "something has failed", "error_detail": str(e)}
    
    def language_categorizer(self):
        languages = [
            repo["language"]
            for repo in self.repos
            if repo["language"]
        ]

        counts = Counter(languages)

        return [
            {
                "language": language,
                "count": count
            }
            for language, count in counts.items()
        ]