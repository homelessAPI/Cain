

from services.repo_analyser import RepoAnalyser
from services.dataCompile import FetchData


class RepositoryQualityAnalyzer:
    def __init__(self, repo):
        self.repo = repo
        self.analyser = RepoAnalyser(repo)
        self.fetcher = FetchData(repo.get("owner", {}).get("login", ""))

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
        repo_readme_score = 0

        for repo_name, content in contents_dict.items():
            if "decoded_content" in content:
                readme_content = content["decoded_content"]
                readme_length = len(readme_content)
                readme_quality = "Good" if readme_length > 100 else "Poor"
                readme_quality_dict[repo_name] = readme_quality

                readme_content = readme_content.replace(" ", "")

                if "##features" in readme_content.lower():
                    repo_readme_score += 1
                if "##installation" in readme_content.lower():
                    repo_readme_score += 1
                if "##usage" in readme_content.lower():
                    repo_readme_score += 1
                if "##tech stack" in readme_content.lower():
                    repo_readme_score += 1
                if "##license" in readme_content.lower():
                    repo_readme_score += 1
                
            else:
                contents_dict[repo_name]["readme_quality"] = "No README"
                readme_quality_dict[repo_name] = "No README"
        return readme_quality_dict, repo_readme_score
