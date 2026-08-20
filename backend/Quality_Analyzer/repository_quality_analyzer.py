from services.repo_analyser import RepoAnalyser


class RepositoryQualityAnalyzer:
    CATEGORY_MAX_SCORES = {
        "documentation": 30,
        "engineering": 30,
        "repo_hygiene": 20,
        "devops": 20
    }

    def __init__(self, username, repos):
        self.username = username
        self.repos = repos
        self.total_repo_score = sum(self.CATEGORY_MAX_SCORES.values())
        self.percentage_repo_score = 0
        self.assigned_letter = None
        self.score_dict = {}
        self.categories = {}

    def analyze(self):
        repos_analyser = RepoAnalyser(self.repos)

        for repo in self.repos:
            repo_name = repo["Repo_name"]

            repo_data = repos_analyser.repo_content_review(
                self.username,
                repo_name
            )

            documentation_score = (
                self.CATEGORY_MAX_SCORES["documentation"]
                if repo_data["README.md"]
                else 0
            )

            repo_hygiene_score = 0
            if repo_data[".gitignore"]:
                repo_hygiene_score += 10
            if repo_data["LICENSE"]:
                repo_hygiene_score += 10

            engineering_score = (
                self.CATEGORY_MAX_SCORES["engineering"]
                if repo_data["Tests"]
                else 0
            )

            devops_score = (
                self.CATEGORY_MAX_SCORES["devops"]
                if repo_data["Dockerfile"]
                else 0
            )

            self.score_dict[repo_name] = {
                "documentation": documentation_score,
                "engineering": engineering_score,
                "repo_hygiene": repo_hygiene_score,
                "devops": devops_score
            }

        print("score dict: " + str(self.score_dict))
        return self.score_dict

    def overall_score(self):
        total_repos = len(self.score_dict)

        if total_repos == 0:
            self.percentage_repo_score = 0
            self.assigned_letter = "N/A"
            self.categories = {
                "documentation": 0,
                "engineering": 0,
                "repo_hygiene": 0,
                "devops": 0
            }

            return {
                "Score": 0,
                "Grade": "N/A",
                "Categories": self.categories
            }

        repos_score = 0
        category_totals = {
            "documentation": 0,
            "engineering": 0,
            "repo_hygiene": 0,
            "devops": 0
        }

        for repo_score in self.score_dict.values():
            repos_score += sum(repo_score.values())

            for category, score in repo_score.items():
                category_totals[category] += score

        self.categories = {
            category: (
                total / (maximum * total_repos)
            ) * 100
            for category, total in category_totals.items()
            for maximum in [self.CATEGORY_MAX_SCORES[category]]
        }

        total_possible_score = self.total_repo_score * total_repos

        self.percentage_repo_score = (
            repos_score / total_possible_score
        ) * 100

        if self.percentage_repo_score >= 90:
            self.assigned_letter = "A"
        elif self.percentage_repo_score >= 80:
            self.assigned_letter = "B"
        elif self.percentage_repo_score >= 70:
            self.assigned_letter = "C"
        elif self.percentage_repo_score >= 60:
            self.assigned_letter = "D"
        else:
            self.assigned_letter = "F"

        return {
            "Score": self.percentage_repo_score,
            "Grade": self.assigned_letter,
            "Categories": self.categories
        }
