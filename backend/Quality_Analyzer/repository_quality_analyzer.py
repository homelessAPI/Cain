from services.repo_analyser import RepoAnalyser
from services.dataCompile import FetchData

class QuslityAnanlysis:
    def __init__(self, username):
        self.username = username

        self.Documentation_score = 0
        self.Engineering_score = 0
        self.Repo_hygiene_score = 0
        self.DevOps_score = 0
        self.Score_dict = {}

    def documentation(self):
        Fetchdata = FetchData(self.username)
        repos = Fetchdata.repos()
        repos_analyser = RepoAnalyser(repos)

        for i in repos:
            repo_documentation_data = repos_analyser.repo_content_review(self.username, i["Repo_name"])

            if repo_documentation_data["README"] == True:
                self.documentation_score += 10

            if repo_documentation_data[".gitignore"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["LICENSE"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["Tests"] == True:
                self.Engineering_score += 10

            if repo_documentation_data["Dockerfile"] == True:
                self.DevOps += 10

            self.Score_dict[i["Repo_name"]] + " documentation" = self.documentation_score
            self.Score_dict[i["Repo_name"]] + " Engineering" = self.Engineering_score
            self.Score_dict[i["Repo_name"]] + " Repo_hygiene" = self.Repo_hygiene_score
            self.Score_dict[i["Repo_name"]] + " DevOps" = self.DevOps_score
            self.documentation_score = 0

        return self.documentation_score_dict
