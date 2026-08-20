from services.repo_analyser import RepoAnalyser


class RepositoryQualityAnalyzer:
    def __init__(self, username, repos):
        self.username = username
        self.repos = repos

        self.documentation_score = 0
        self.engineering_score = 0
        self.repo_hygiene_score = 0
        self.devops_score = 0

        self.total_repo_score = 100
        self.percentage_repo_score = 0
        self.assigned_letter = None

        self.score_dict = {}

    def analyze(self):
        repos_analyser = RepoAnalyser(self.repos)

        for repo in self.repos:
            repo_name = repo["Repo_name"]

            repo_data = repos_analyser.repo_content_review(
                self.username,
                repo_name
            )

            if repo_data["README.md"]:
                self.documentation_score += 30

            if repo_data[".gitignore"]:
                self.repo_hygiene_score += 10

            if repo_data["LICENSE"]:
                self.repo_hygiene_score += 10

            if repo_data["Tests"]:
                self.engineering_score += 30

            if repo_data["Dockerfile"]:
                self.devops_score += 20

            self.score_dict[repo_name] = {
                "documentation": self.documentation_score,
                "engineering": self.engineering_score,
                "repo_hygiene": self.repo_hygiene_score,
                "devops": self.devops_score
            }

            # Reset category scores before analyzing the next repository.
            self.documentation_score = 0
            self.engineering_score = 0
            self.repo_hygiene_score = 0
            self.devops_score = 0

        print("score dict: " + str(self.score_dict))
        return self.score_dict

    def overall_score(self):
        total_repos = len(self.score_dict)

        # A user can legitimately have zero public repositories.
        if total_repos == 0:
            self.percentage_repo_score = 0
            self.assigned_letter = "N/A"

            return {
                "Score": 0,
                "Grade": "N/A",
                
            }

        repos_score = 0

        for repo_score in self.score_dict.values():
            repos_score += sum(repo_score.values())

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
            "Grade": self.assigned_letter
        }