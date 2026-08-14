from services.repo_analyser import repo_content_review
from services.dataCompile import FetchData

class QuslityAnanlysis:
    def __init__(self, username):
        self.username = username

        self.documentation_score = 0

    def documentation(self):
        Fetchdata = FetchData(self.username)
        repos = Fetchdata.repos()

        for i in repos:
            repo_documentation_data = repo_content_review(i["Repo_name"])

            if repo_documentation_data["README"] == True:
                self.documentation_score += 10

            elif repo_documentation_data[".gitignore"] == True:
                self.documentation_score += 10

            elif repo_documentation_data["LICENSE"] == True:
                self.documentation_score += 10

            elif repo_documentation_data["Tests"] == True:
                self.documentation_score += 10

            elif repo_documentation_data["Dockerfile"] == True:
                self.documentation_score += 10

        return self.documentation_score