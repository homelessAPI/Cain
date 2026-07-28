def build_review_prompt(user, repos, events):

    return f"""
You are a senior software engineer.

Review this GitHub profile.

Followers:
{user["followers"]}

Following:
{user["following"]}

Repositories:
{repos}

Recent Events:
{events}

Tell me:

1. Strengths
2. Weaknesses
3. Technologies missing
4. Project ideas
5. Rating out of 10
"""