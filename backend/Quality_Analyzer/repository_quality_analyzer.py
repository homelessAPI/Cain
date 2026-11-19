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

    def readme_quality(self, contents_dict=None):
        if contents_dict is None:
            contents_dict = self.fetcher.repo_contents()

        readme_quality_dict = {}
        repo_readme_score = {}
        readme_reasons = {}

        sections = [
            "features",
            "installation",
            "usage",
            "tech stack",
            "license"
        ]

        for repo_name, readme_content in contents_dict.items():
            repo_readme_score[repo_name] = 0
            readme_reasons[repo_name] = {
                "earned": [],
                "missing": []
            }

            if not readme_content:
                readme_quality_dict[repo_name] = "No README"

                for section in sections:
                    readme_reasons[repo_name]["missing"].append(
                        f"Missing {section.title()} section."
                    )

                continue

            lines = readme_content.lower().splitlines()

            for section in sections:
                section_found = False
                section_has_content = False

                for index, line in enumerate(lines):
                    heading = line.strip().lstrip("#").strip()

                    if heading == section and line.strip().startswith("#"):
                        section_found = True

                        for next_line in lines[index + 1:]:
                            next_heading = next_line.strip()

                            if next_heading.startswith("#"):
                                break

                            if next_heading:
                                section_has_content = True
                                break

                        break

                if section_found and section_has_content:
                    repo_readme_score[repo_name] += 1
                    readme_reasons[repo_name]["earned"].append(
                        f"{section.title()}: section found with content."
                    )
                elif section_found:
                    readme_reasons[repo_name]["missing"].append(
                        f"{section.title()}: heading found, but no content follows it."
                    )
                else:
                    readme_reasons[repo_name]["missing"].append(
                        f"Missing {section.title()} section."
                    )

            score = repo_readme_score[repo_name]

            if score == 5:
                readme_quality_dict[repo_name] = "Excellent"
            elif score == 4:
                readme_quality_dict[repo_name] = "Good"
            elif score == 3:
                readme_quality_dict[repo_name] = "Fair"
            else:
                readme_quality_dict[repo_name] = "Needs work"

        total_readme_score = sum(repo_readme_score.values())

        return (
            readme_quality_dict,
            repo_readme_score,
            readme_reasons,
            total_readme_score
        )
