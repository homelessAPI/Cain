from services.repo_analyser import RepoAnalyser
from services.dataCompile import FetchData


class RepositoryQualityAnalyzer:
    def __init__(self, repo):
        self.repo = repo
        owner = repo.get("owner", "")
        if isinstance(owner, dict):
            owner = owner.get("login", "")
        self.fetcher = FetchData(owner)

    def analyze_repository(self):
        analyser = RepoAnalyser(self.repo)
        return {
            "age_in_days": analyser.repository_age(),
            "days_since_last_push": analyser.days_since_last_push(),
            "activity_level": analyser.activity_level()
        }

    def documentation_quality(self, contents_dict=None):
        if contents_dict is None:
            contents_dict = self.fetcher.repo_contents()

        documentation_quality_dict = {}
        repo_documentation_score = {}
        documentation_reasons = {}

        sections = [
            "features",
            "installation",
            "usage",
            "tech stack",
            "license"
        ]

        for repo_name, readme_content in contents_dict.items():
            repo_documentation_score[repo_name] = 0
            documentation_reasons[repo_name] = {
                "earned": [],
                "missing": []
            }

            if not readme_content:
                documentation_quality_dict[repo_name] = "No README"
                for section in sections:
                    documentation_reasons[repo_name]["missing"].append(
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
                    repo_documentation_score[repo_name] += 1
                    documentation_reasons[repo_name]["earned"].append(
                        f"{section.title()}: section found with content."
                    )
                elif section_found:
                    documentation_reasons[repo_name]["missing"].append(
                        f"{section.title()}: heading found, but no content follows it."
                    )
                else:
                    documentation_reasons[repo_name]["missing"].append(
                        f"Missing {section.title()} section."
                    )

            score = repo_documentation_score[repo_name]
            if score == 5:
                documentation_quality_dict[repo_name] = "Excellent"
            elif score == 4:
                documentation_quality_dict[repo_name] = "Good"
            elif score == 3:
                documentation_quality_dict[repo_name] = "Fair"
            else:
                documentation_quality_dict[repo_name] = "Needs work"

        total_score = sum(repo_documentation_score.values())

        return (
            documentation_quality_dict,
            repo_documentation_score,
            documentation_reasons,
            total_score
        )

    def maintenance_quality(self, repos, commit_activity):
        maintenance_results = {}
        total_score = 0
        max_score = 0

        for repo in repos:
            repo_name = repo["Repo_name"]
            activity = commit_activity.get(repo_name, {})
            assessment = RepoAnalyser(repo).maintenance_assessment(activity)
            maintenance_results[repo_name] = assessment

            total_score += assessment["score"] or 0
            max_score += assessment["max_score"]

        percentage = round(total_score / max_score * 100, 1) if max_score else 0

        return {
            "repositories": maintenance_results,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage
        }
