from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import requests
import base64
import re


class FetchData:

    def __init__(self, username: str):
        self.username = username

        self.url = f"https://api.github.com/users/{username}"
        self.events_url = f"https://api.github.com/users/{username}/events"
        self.repos_url = f"https://api.github.com/users/{username}/repos"

    # -------------------------
    # USER
    # -------------------------

    def raise_github_error(self, response, context):
        """Translate GitHub API failures into clear, consistent API errors."""
        message = (response.text or "").lower()
        remaining = response.headers.get("X-RateLimit-Remaining")

        if response.status_code == 404 and context == "user":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "GITHUB_USER_NOT_FOUND",
                    "message": (
                        f'No GitHub account was found for "{self.username}". '
                        "Make sure you entered the username (the @handle/login), "
                        "not the display name shown above it on the profile. "
                        "You can find the username in the profile URL: "
                        "github.com/username."
                    )
                }
            )

        if response.status_code in (403, 429) and (
            response.status_code == 429
            or remaining == "0"
            or "rate limit" in message
            or "secondary rate" in message
        ):
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "GITHUB_RATE_LIMIT",
                    "message": (
                        "GitHub is temporarily limiting requests. "
                        "Please wait a little while before trying again."
                    )
                }
            )

        if response.status_code >= 500:
            raise HTTPException(
                status_code=502,
                detail={
                    "code": "GITHUB_UNAVAILABLE",
                    "message": (
                        "GitHub is currently having trouble responding. "
                        "Please try again in a few minutes."
                    )
                }
            )

        raise HTTPException(
            status_code=502,
            detail={
                "code": "GITHUB_REQUEST_FAILED",
                "message": f"Cain could not retrieve {context} from GitHub."
            }
        )

    def fetch_user_info(self):
        try:
            response = requests.get(self.url, timeout=15)
        except requests.RequestException as error:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "GITHUB_CONNECTION_FAILED",
                    "message": (
                        "Cain could not connect to GitHub. "
                        "GitHub may be temporarily unavailable; please try again."
                    )
                }
            ) from error

        if response.status_code != 200:
            self.raise_github_error(response, "user")

        data = response.json()

        if not data:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "GITHUB_USER_NOT_FOUND",
                    "message": (
                        f'No GitHub account was found for "{self.username}". '
                        "Use the @username/login shown in the profile URL, "
                        "not the display name at the top of the profile."
                    )
                }
            )

        return data

    def user_info(self):
        data = self.fetch_user_info()

        return {
            "profile": data["avatar_url"],
            "following": data["following"],
            "followers": data["followers"],
            "public_repos": data["public_repos"],
            "company": data["company"],
            "hireable": data["hireable"],
            "bio": data["bio"],
            "login": data["login"],
            "name": data.get("name"),
            "created_at": data["created_at"],
            "location": data.get("location")
        }

    # -------------------------
    # EVENTS
    # -------------------------

    def fetch_events_info(self):
        response = requests.get(self.events_url)

        if response.status_code != 200:
            self.raise_github_error(response, "activity data")

        data = response.json()

        return data

    def events(self):
        events_data = self.fetch_events_info()

        if not events_data:
            return []

        events_list = []

        for event in events_data:
            created_at = datetime.fromisoformat(
                event["created_at"].replace("Z", "+00:00")
            )

            events_list.append({
                "type": event["type"],
                "repository": event["repo"]["name"],
                "repository_url": f"https://github.com/{event['repo']['name']}",
                "created_at": created_at,
                "public": event["public"]
            })

        return events_list

    # -------------------------
    # REPOSITORIES
    # -------------------------

    def fetch_repos(self):
        page = 1
        all_repos = []

        while True:
            response = requests.get(
                self.repos_url,
                params={
                    "page": page,
                    "per_page": 100
                }
            )

            if response.status_code != 200:
                self.raise_github_error(response, "repository data")

            data = response.json()

            if not data:
                break

            all_repos.extend(data)
            page += 1

        return all_repos
    
    def fetch_repo_contents(self, repo_name):
        branch = "main"  
        repo_contents_url = f"https://api.github.com/repos/{self.username}/{repo_name}/git/trees/{branch}?recursive=1"

        response = requests.get(
            repo_contents_url.format(repo_name=repo_name)
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to retrieve contents for repo: {repo_name}"
            )

        data = response.json()

        return data
    
    def repos(self):
        repos_data = self.fetch_repos()
        repos_list = []

        for repo in repos_data:
            repos_list.append({
                "Repo_name": repo["name"],
                "description": repo["description"],
                "Private": repo["private"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "forks": repo["forks"],
                "stargazers_count": repo["stargazers_count"],
                "watchers_count": repo["watchers_count"],
                "size": repo["size"],
                "default_branch": repo["default_branch"],
                "open_issues_count": repo["open_issues_count"],
                "pushed_at": repo["pushed_at"],
                "archived": repo["archived"],
                "owner": repo["owner"]["login"],
                "language": repo["language"],
                "repo_url": repo["html_url"],
                "license": (repo.get("license") or {}).get("spdx_id"),
                "fork": repo.get("fork", False)
            })

            
        return repos_list


    # -------------------------
    # COMMIT HISTORY
    # -------------------------

    def repo_commit_activity(self, repos_list):
        """
        Collect up to 100 commits from the last six months for each repository.
        Active months are used as a simple measure of contribution frequency.
        """
        since = datetime.now(timezone.utc) - timedelta(days=183)
        activity = {}

        for repo in repos_list:
            repo_name = repo["Repo_name"]

            if repo.get("archived"):
                activity[repo_name] = {
                    "available": False,
                    "archived": True,
                    "commit_count": 0,
                    "active_months": 0,
                    "history_capped": False
                }
                continue

            commits_url = (
                f"https://api.github.com/repos/{self.username}/"
                f"{repo_name}/commits"
            )

            try:
                response = requests.get(
                    commits_url,
                    params={
                        "since": since.isoformat(),
                        "per_page": 100,
                        "sha": repo.get("default_branch", "main")
                    },
                    timeout=15
                )

                if response.status_code != 200:
                    activity[repo_name] = {
                        "available": False,
                        "archived": False,
                        "commit_count": 0,
                        "active_months": 0,
                        "history_capped": False
                    }
                    continue

                commits = response.json()
                active_months = set()

                for commit in commits:
                    commit_data = commit.get("commit", {})
                    author_data = commit_data.get("author") or {}
                    committer_data = commit_data.get("committer") or {}
                    commit_date = (
                        author_data.get("date")
                        or committer_data.get("date")
                    )

                    if not commit_date:
                        continue

                    parsed_date = datetime.fromisoformat(
                        commit_date.replace("Z", "+00:00")
                    )
                    active_months.add(parsed_date.strftime("%Y-%m"))

                activity[repo_name] = {
                    "available": True,
                    "archived": False,
                    "commit_count": len(commits),
                    "active_months": len(active_months),
                    "history_capped": len(commits) == 100
                }

            except (requests.RequestException, ValueError, TypeError):
                activity[repo_name] = {
                    "available": False,
                    "archived": False,
                    "commit_count": 0,
                    "active_months": 0,
                    "history_capped": False
                }

        return activity


    # -------------------------
    # PROJECT FILE TREES
    # -------------------------

    def repo_trees(self, repos_list, pinned_repositories=None, limit=30):
        """Fetch file paths and sizes, prioritizing recent and pinned projects."""
        trees = {}
        recent_repos = sorted(
            repos_list,
            key=lambda repo: repo.get("pushed_at") or "",
            reverse=True
        )[:limit]

        pinned_names = {
            name.rsplit("/", 1)[-1].lower()
            for name in (pinned_repositories or [])
        }
        pinned_repos = [
            repo for repo in repos_list
            if repo["Repo_name"].lower() in pinned_names
        ]
        selected_repos = {
            repo["Repo_name"]: repo for repo in recent_repos + pinned_repos
        }
        scanned_repos = list(selected_repos.values())

        for repo in scanned_repos:
            repo_name = repo["Repo_name"]
            branch = repo.get("default_branch") or "main"
            tree_url = (
                f"https://api.github.com/repos/{self.username}/"
                f"{repo_name}/git/trees/{branch}"
            )

            try:
                response = requests.get(
                    tree_url,
                    params={"recursive": "1"},
                    timeout=15
                )
                if response.status_code != 200:
                    trees[repo_name] = {"available": False, "files": [], "truncated": False}
                    continue

                tree_data = response.json()
                trees[repo_name] = {
                    "available": True,
                    "files": [
                        item for item in tree_data.get("tree", [])
                        if item.get("type") == "blob"
                    ],
                    "truncated": tree_data.get("truncated", False)
                }
            except (requests.RequestException, ValueError):
                trees[repo_name] = {"available": False, "files": [], "truncated": False}

        return {
            "repositories": trees,
            "scanned_count": len(trees),
            "total_count": len(repos_list),
            "scan_limit": limit
        }

    # -------------------------
    # PROFILE SIGNALS
    # -------------------------

    def pull_request_activity(self):
        url = "https://api.github.com/search/issues"
        headers = {"Accept": "application/vnd.github+json"}
        counts = {}

        for label, qualifier in [("total", ""), ("merged", " is:merged")]:
            try:
                response = requests.get(
                    url,
                    params={
                        "q": f"author:{self.username} is:pr{qualifier}",
                        "per_page": 1
                    },
                    headers=headers,
                    timeout=12
                )
                counts[label] = (
                    response.json().get("total_count", 0)
                    if response.status_code == 200 else None
                )
            except (requests.RequestException, ValueError):
                counts[label] = None

        counts["available"] = counts["total"] is not None
        return counts

    def pinned_repositories(self):
        """
        Pinned repositories are not exposed by GitHub's public REST API.
        Inspect the public profile page and return None if unavailable.
        """
        try:
            response = requests.get(
                f"https://github.com/{self.username}",
                headers={"User-Agent": "Cain-GitHub-Analyzer"},
                timeout=12
            )
            if response.status_code != 200:
                return None

            cards = re.findall(
                r'pinned-item-list-item-content(.*?)(?=pinned-item-list-item-content|</li>)',
                response.text,
                flags=re.IGNORECASE | re.DOTALL
            )
            pinned = []

            for card in cards:
                match = re.search(
                    r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"',
                    card
                )
                if match:
                    repo_name = match.group(1).rstrip("/")
                    if repo_name not in pinned:
                        pinned.append(repo_name)

            return pinned
        except requests.RequestException:
            return None

    # -------------------------
    # REPOSITORY CONTENTS
    # -------------------------

    def repo_contents(self, repos_list=None):

        repos_contents = self.fetch_repos() if repos_list is None else repos_list
        print(f"repos_contents: {repos_contents}")

        if repos_list is None:
            repos_list = self.repos()
        Readme_dict = {}
        Readme_Content = {}

        for repo in repos_list:
            readme_url = f"https://api.github.com/repos/{self.username}/{repo['Repo_name']}/readme"
            readme_response = requests.get(readme_url)
            Readme_dict[repo["Repo_name"]] = readme_response.json()

        for repo_name, readme_data in Readme_dict.items():
            if "content" in readme_data:
                content = readme_data["content"]
                decoded_content = base64.b64decode(content).decode("utf-8")
                Readme_Content[repo_name] = decoded_content
                Readme_dict[repo_name]["decoded_content"] = decoded_content
            else:
                Readme_dict[repo_name]["decoded_content"] = None
                Readme_Content[repo_name] = None

        #print(f"Readme_Content: {Readme_Content}")

        return Readme_Content

    