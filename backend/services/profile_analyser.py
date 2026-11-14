from services.dataCompile import FetchData

class ProfileAnalyser:
    def __init__(self, username):
        self.username = username
        self.fetcher = FetchData(username)

    def analyze_profile(self):
        user_info = self.fetcher.user_info()
        events = self.fetcher.events()

        return {
            "user_info": user_info,
            "events": events,
        }