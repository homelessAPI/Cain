import re
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


    def project_hygiene_quality(self, repos, tree_data):
        """Score tracked repository files for hygiene, out of 10 per repository."""
        results = {}
        total_score = 0
        max_score = 0
        scanned = tree_data.get("repositories", {})

        manifests = {
            "package.json", "requirements.txt", "pyproject.toml", "pipfile",
            "cargo.toml", "go.mod", "pom.xml", "build.gradle",
            "build.gradle.kts", "gemfile", "composer.json", "mix.exs",
            "pubspec.yaml"
        }
        lockfiles = {
            "package-lock.json", "npm-shrinkwrap.json", "yarn.lock",
            "pnpm-lock.yaml", "poetry.lock", "uv.lock", "pipfile.lock",
            "cargo.lock", "go.sum", "composer.lock", "gemfile.lock"
        }
        quality_configs = (
            ".eslintrc", ".prettierrc", "ruff.toml", ".editorconfig",
            ".pre-commit-config.yaml", "eslint.config.", "prettier.config."
        )
        secret_names = {
            "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "credentials.json"
        }
        binary_extensions = {
            ".exe", ".dll", ".so", ".dylib", ".bin",
            ".zip", ".7z", ".rar", ".tar", ".gz"
        }

        for repo in repos:
            repo_name = repo["Repo_name"]
            tree = scanned.get(repo_name)

            if not tree or not tree.get("available"):
                results[repo_name] = {
                    "available": False, "score": None, "max_score": 10,
                    "findings": [], "good_signs": [],
                    "missing_signs": ["Repository file tree could not be inspected."],
                    "truncated": False
                }
                continue

            files = tree.get("files", [])
            paths = [item.get("path", "") for item in files]
            lower_paths = [path.lower() for path in paths]
            basenames = [path.rsplit("/", 1)[-1].lower() for path in paths]
            findings, good_signs, missing_signs = [], [], []
            deductions = 0.0

            def add_finding(path, severity, message, points):
                nonlocal deductions
                findings.append({
                    "path": path, "severity": severity, "message": message
                })
                deductions += points

            for item in files:
                path = item.get("path", "")
                lowered = path.lower()
                basename = lowered.rsplit("/", 1)[-1]
                segments = lowered.split("/")

                if any(part in {"node_modules", "venv", ".venv", "__pycache__"} for part in segments):
                    add_finding(path, "High", "Generated dependencies or Python cache files are committed.", 1.5)
                elif any(part in {".idea", ".vscode"} for part in segments):
                    add_finding(path, "Low", "Editor-specific settings are committed; consider whether they belong here.", 0.25)
                if basename == ".ds_store":
                    add_finding(path, "Low", "Operating-system metadata should not usually be committed.", 0.25)

                if basename == ".env" or (
                    basename.startswith(".env.")
                    and basename not in {".env.example", ".env.sample", ".env.template"}
                ):
                    add_finding(path, "Critical", "An environment file that may contain secrets is tracked. Inspect it and rotate exposed credentials.", 3)

                if (
                    basename in secret_names
                    or basename.endswith(".pem")
                    or basename.startswith("secrets.")
                    or basename == "credentials"
                ):
                    add_finding(path, "Critical", "A filename commonly associated with private keys or credentials is tracked. Inspect it immediately.", 3)

                if any(part in {"dist", "build"} for part in segments):
                    add_finding(path, "Medium", "A generated build-output directory is tracked; confirm that this is intentional.", 0.75)

                size = item.get("size") or 0
                extension = "." + basename.rsplit(".", 1)[-1] if "." in basename else ""
                if extension in binary_extensions:
                    add_finding(path, "Medium", f"Archive or executable file is tracked ({size:,} bytes).", 0.75 if size < 5_000_000 else 1.25)
                elif size >= 5_000_000:
                    add_finding(path, "Medium", f"Large file is tracked ({size / 1_000_000:.1f} MB); consider Git LFS or external storage.", 1)

                if (
                    basename.startswith("untitled")
                    or basename.startswith("copy of ")
                    or re.match(r"^(final_v\d|final_.*real|final_v\d+_real|copy_?\d)", basename)
                ):
                    add_finding(path, "Low", "Filename looks temporary or like an unfinalized copy.", 0.5)

            def has_name(name):
                return any(path == name or path.endswith("/" + name) for path in lower_paths)

            has_gitignore = has_name(".gitignore")
            has_license = bool(repo.get("license")) or any(
                name in {"license", "license.md", "license.txt"} for name in basenames
            )
            has_manifest = any(name in manifests for name in basenames)
            has_lockfile = any(name in lockfiles for name in basenames)
            has_quality_config = any(
                any(config in name for config in quality_configs)
                for name in basenames
            )
            has_env_example = any(
                name in {".env.example", ".env.sample", ".env.template"}
                for name in basenames
            )

            if has_gitignore:
                good_signs.append(".gitignore is present.")
            else:
                missing_signs.append("Add a .gitignore for generated files, local environments, and secrets.")

            if has_license:
                good_signs.append("A license is declared or a LICENSE file is present.")
            else:
                missing_signs.append("Consider adding a LICENSE file so reuse terms are clear.")

            if has_manifest:
                good_signs.append("A dependency or build manifest is present.")
            else:
                missing_signs.append("No common dependency manifest was detected; add one if this project uses external dependencies.")

            if has_lockfile:
                good_signs.append("A dependency lockfile is present.")
            else:
                missing_signs.append("No common dependency lockfile was detected.")

            if has_quality_config:
                good_signs.append("A code-quality or editor configuration file is present.")
            else:
                missing_signs.append("Consider adding linting, formatting, or editor configuration.")

            if has_env_example:
                good_signs.append("An example environment file documents configuration.")
            else:
                missing_signs.append("If environment variables are required, consider providing a safe .env.example.")

            score = 4.5
            score += 1.5 if has_gitignore else 0
            score += 1.0 if has_license else 0
            score += 1.0 if has_manifest else 0
            score += 0.75 if has_lockfile else 0
            score += 0.75 if has_quality_config else 0
            score += 0.5 if has_env_example else 0
            score = max(0, min(10, round(score - deductions, 1)))

            results[repo_name] = {
                "available": True,
                "score": score,
                "max_score": 10,
                "grade": (
                    "Excellent" if score >= 9 else
                    "Good" if score >= 7 else
                    "Fair" if score >= 5 else "Needs work"
                ),
                "findings": findings,
                "good_signs": good_signs,
                "missing_signs": missing_signs,
                "truncated": tree.get("truncated", False)
            }
            total_score += score
            max_score += 10

        percentage = round(total_score / max_score * 100, 1) if max_score else 0
        return {
            "repositories": results,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "scanned_count": tree_data.get("scanned_count", 0),
            "total_count": tree_data.get("total_count", len(repos))
        }

    def profile_level_assessment(
        self, user_profile, repos, events, pull_requests,
        pinned_repositories, documentation_scores, hygiene_results
    ):
        """Calculate an internal profile percentage but show qualitative feedback."""
        from datetime import datetime, timezone

        created_at = user_profile.get("created_at")
        account_age_days = None
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                account_age_days = (datetime.now(timezone.utc) - created_date).days
            except ValueError:
                pass

        languages = sorted({
            repo.get("language") for repo in repos if repo.get("language")
        })
        public_events = len(events or [])
        push_events = sum(1 for event in (events or []) if event.get("type") == "PushEvent")
        pr_events = sum(1 for event in (events or []) if event.get("type") == "PullRequestEvent")
        profile_score = 0.0
        available_weight = 0.0
        improvements, strengths = [], []

        if pull_requests.get("available"):
            pr_count = pull_requests.get("total") or 0
            merged_count = pull_requests.get("merged") or 0
            profile_score += min(pr_count / 5, 1) * 15 + min(merged_count / 3, 1) * 10
            available_weight += 25
            if pr_count:
                strengths.append(f"{pr_count} public pull request(s), including {merged_count} merged.")
            else:
                improvements.append("No public pull requests were found. Contributing to another project through a pull request can demonstrate collaboration.")
        else:
            improvements.append("Pull request activity could not be verified from GitHub.")

        profile_score += min(public_events / 40, 1) * 12 + min(push_events / 20, 1) * 8
        available_weight += 20
        if public_events:
            strengths.append(f"{public_events} recent public events were visible, including {push_events} push events.")
        else:
            improvements.append("Little or no recent public contribution activity was visible. GitHub's public events endpoint is limited to recent activity, not lifetime contributions.")

        if pinned_repositories is not None:
            available_weight += 15
            if pinned_repositories:
                profile_score += 15
                strengths.append(f"{len(pinned_repositories)} pinned repository/repositories found.")
            else:
                improvements.append("No pinned repositories were detected. Pin your strongest projects so visitors can find your best work quickly.")
        else:
            improvements.append("Pinned repositories could not be inspected automatically; verify your profile pins manually.")

        profile_score += min(len(languages) / 4, 1) * 15
        available_weight += 15
        if len(languages) >= 2:
            strengths.append(f"{len(languages)} programming languages detected across public repositories.")
        elif len(languages) == 1:
            improvements.append(f"Only {languages[0]} was detected as a primary repository language. Demonstrate depth first; additional languages are optional.")
        else:
            improvements.append("No primary programming languages were detected across public repositories.")

        repo_quality = []
        for repo in repos:
            name = repo["Repo_name"]
            doc_score = documentation_scores.get(name)
            hygiene = hygiene_results.get("repositories", {}).get(name, {})
            hygiene_score = hygiene.get("score")
            if doc_score is not None and hygiene_score is not None:
                repo_quality.append((doc_score / 5 * 100 + hygiene_score / 10 * 100) / 2)

        if repo_quality:
            best_project = max(repo_quality)
            profile_score += best_project / 100 * 15
            available_weight += 15
            if best_project >= 80:
                strengths.append("At least one repository has strong documentation and project hygiene.")
            else:
                improvements.append("Improve the documentation and project hygiene of your strongest project so it makes a better first impression.")
        else:
            improvements.append("A standout project could not be assessed because repository file data was unavailable.")

        # Account age is context, not a penalty. A young account can earn
        # a small recognition bonus when it already has a strong flagship project.
        if account_age_days is not None and account_age_days <= 180:
            if repo_quality and max(repo_quality) >= 80:
                profile_score += 10
                available_weight += 10
                strengths.append("Strong project presentation on a young account is recognized as early achievement.")
            else:
                improvements.append("For a newer account, a polished flagship repository can demonstrate strong early progress.")

        percentage = round(profile_score / available_weight * 100, 1) if available_weight else 0
        level = "Strong profile" if percentage >= 85 else "Developing profile" if percentage >= 70 else "Profile needs attention"

        if account_age_days is None:
            account_age = "Unavailable"
        elif account_age_days < 30:
            account_age = f"{account_age_days} days"
        elif account_age_days < 365:
            account_age = f"{round(account_age_days / 30)} months"
        else:
            account_age = f"{round(account_age_days / 365, 1)} years"

        return {
            "internal_percentage": percentage,
            "level": level,
            "account_age": account_age,
            "account_age_days": account_age_days,
            "public_pull_requests": pull_requests.get("total"),
            "merged_pull_requests": pull_requests.get("merged"),
            "recent_public_events": public_events,
            "recent_push_events": push_events,
            "recent_pull_request_events": pr_events,
            "pinned_repositories": pinned_repositories,
            "languages": languages,
            "strengths": strengths,
            "improvements": improvements,
            "note": "Account age is context, not a direct score. Public event data is recent and capped; private contributions are not visible."
        }

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
