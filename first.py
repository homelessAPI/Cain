import requests
from tabulate import tabulate



def github_activity(username):
    url = f"https://api.github.com/users/{username}"
    events_url = f"https://api.github.com/users/{username}/events"
    repos_url = f"https://api.github.com/users/{username}/repos"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            events_response = requests.get(events_url, timeout=10)

            if events_response.status_code != 200:
                print(f"Failed to retrieve events. Status code: {events_response.status_code}")
            elif events_response.json() == []:
                print(f"No events found for user '{username}'.")
            else:
                events = []
                for i in events_response.json():
                    events.append({
                        "type": i["type"],
                        "repository": i["repo"]["name"],
                        "repository_url": i["repo"]["url"],
                        "created_at": i["created_at"],
                        "public": i["public"]
                })

                return {"events": events}

        else:
            print(f"Failed to retrieve data for user. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred while making the API request: {e}")

if __name__ == "__main__":
    while True:
        username = input("Enter a GitHub username (or 'exit' to quit): ")
        if username.lower() == 'exit':
            break
        github_activity(username)