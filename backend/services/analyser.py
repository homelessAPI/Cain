from datetime import datetime

class GitHubAnalyzer:

    def __init__(self, events):
        self.events = events

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