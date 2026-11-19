from services.repo_analyser import RepoAnalyser
from services.dataCompile import FetchData


class RepositoryQualityAnalyzer:
    def __init__(self, repo):
        self.repo = repo
        self.analyser = RepoAnalyser(repo)

        owner = repo.get("owner", "")
        if isinstance(owner, dict):
            owner = owner.get("login", "")

        self.fetcher = FetchData(owner)

    def analyze_repository(self):
        age = self.analyser.repository_age()
        days_since_push = self.analyser.days_since_last_push()
        activity_level = self.analyser.activity_level()

        return {
            "age_in_days": age,
            "days_since_last_push": days_since_push,
            "activity_level": activity_level
        }

    def readme_quality(self):
        contents_dict = self.fetcher.repo_contents()
        readme_quality_dict = {}
        repo_readme_score = {}

        sections = [
            "features",
            "installation",
            "usage",
            "tech stack",
            "license"
        ]

        for repo_name, readme_content in contents_dict.items():
            if not readme_content:
                readme_quality_dict[repo_name] = "No README"
                repo_readme_score[repo_name] = 0
                continue

            readme_content = readme_content.lower()
            repo_readme_score[repo_name] = 0

            for section in sections:
                if any(
                    line.strip().lstrip("#").strip() == section
                    for line in readme_content.splitlines()
                ):
                    repo_readme_score[repo_name] += 1

            readme_quality = "Good" if repo_readme_score[repo_name] >= 3 else "Poor"
            readme_quality_dict[repo_name] = readme_quality

        return readme_quality_dict, repo_readme_score
