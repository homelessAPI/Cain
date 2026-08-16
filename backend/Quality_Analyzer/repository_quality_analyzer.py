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
                self.Documentation_score += 10

            if repo_documentation_data[".gitignore"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["LICENSE"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["Tests"] == True:
                self.Engineering_score += 10

            if repo_documentation_data["Dockerfile"] == True:
                self.DevOps_score += 10

            self.Score_dict[i["Repo_name"]] = {"documentation": self.Documentation_score,
                                               "Engineering_score": self.Engineering_score,
                                               "Repo_hygiene_score": self.Repo_hygiene_score,
                                               "DevOps_score": self.DevOps_score
                                               }
            self.documentation_score = 0

        return self.Score_dict

