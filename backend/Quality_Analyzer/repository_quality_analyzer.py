from services.repo_analyser import RepoAnalyser
from services.dataCompile import FetchData

class QuslityAnanlysis:
    def __init__(self, username):
        self.username = username

        self.Fetchdata = FetchData(self.username)
        self.repos = self.Fetchdata.repos()

        self.Documentation_score = 0
        self.Engineering_score = 0
        self.Repo_hygiene_score = 0
        self.DevOps_score = 0

        self.total_repo_score = 100
        self.percentage_repo_Score = 0
        self.assigned_letter

        self.Score_dict = {}

    def documentation(self):
        repos_analyser = RepoAnalyser(self.repos)

        for i in self.repos:
            repo_documentation_data = repos_analyser.repo_content_review(self.username, i["Repo_name"])

            if repo_documentation_data["README"] == True:
                self.Documentation_score += 30

            if repo_documentation_data[".gitignore"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["LICENSE"] == True:
                self.Repo_hygiene_score += 10

            if repo_documentation_data["Tests"] == True:
                self.Engineering_score += 30

            if repo_documentation_data["Dockerfile"] == True:
                self.DevOps_score += 20

            self.Score_dict[i["Repo_name"]] = {"documentation": self.Documentation_score,
                                               "Engineering_score": self.Engineering_score,
                                               "Repo_hygiene_score": self.Repo_hygiene_score,
                                               "DevOps_score": self.DevOps_score
                                               }
            self.Documentation_score = 0
            self.Engineering_score = 0
            self.Repo_hygiene_score = 0
            self.DevOps_score = 0

        return self.Score_dict

    def Overall_Score(self):
        total_repos = len(self.Score_dict)
        total_possible_score = self.total_repo_score * total_repos

        repos_score = 0

        for i in self.Score_dict:
            repos_score += sum(i.values())

        self.percentage_repo_Score = (repos_score/total_possible_score) * 100

        if 90 <= self.percentage_repo_Score <= 100:
            self.assigned_letter = "A"

        if 80 <= self.percentage_repo_Score <= 89:
                    self.assigned_letter = "B"

        if 70 <= self.percentage_repo_Score <= 79:
                    self.assigned_letter = "C"

        if 60 <= self.percentage_repo_Score <= 69:
                    self.assigned_letter = "D"

        return self.percentage_repo_Score