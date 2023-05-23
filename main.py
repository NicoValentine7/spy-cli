#!/usr/bin/env python3
import os
import sys
import argparse
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup necessary variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"
USERNAME = os.getenv("GITHUB_USERNAME")

# Check the GitHub token and username
print("GitHub Token: ", os.getenv("GITHUB_TOKEN"))
print("GitHub Username: ", os.getenv("GITHUB_USERNAME"))
if GITHUB_TOKEN is None or USERNAME is None:
    print("ERROR: GitHub token and username are required.")
    sys.exit(1)


def send_github_request(endpoint, method, headers, json=None):
    """
    Sends a request to the GitHub API.
    """
    url = GITHUB_API_URL + endpoint
    response = requests.request(method, url, headers=headers, json=json)

    print(f"Request sent to URL: {url}")  # Debug print
    print(f"Response status code: {response.status_code}")  # Debug print
    if response.text:
        print(f"Response text: {response.text}")  # Debug print

    return response


def create_github_repo(repo_name):
    """
    Create a new GitHub repository.
    """
    headers = {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"name": "SPY-" + repo_name, "private": True}
    response = send_github_request("/user/repos", "POST", headers, data)

    if response.status_code == 201:
        print(f"Successfully created repository SPY-{repo_name}")
        return response.json()["ssh_url"]
    else:
        print(f"ERROR: Failed to create repository SPY-{repo_name}")
        # Print full response content for debugging
        print(f"Full response content: {response.content}")

        return None

    """
    Create a new GitHub repository.
    """
    headers = {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"name": "SPY-" + repo_name, "private": True}
    response = send_github_request("/user/repos", "POST", headers, data)

    if response.status_code == 201:
        ssh_url = response.json()["ssh_url"]
        print(f"Successfully created repository SPY-{repo_name}")
        print(f"Repository owner: {USERNAME}")
        print(f"Repository URL: {ssh_url}")
        return ssh_url
    else:
        print(f"ERROR: Failed to create repository SPY-{repo_name}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return None


def update_spy_list(repo_name, ssh_url):
    """
    Update the SPY-LIST with the new repository.
    """
    headers = {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "message": f"Add SPY-{repo_name}",
        "content": base64.b64encode(
            f"[SPY-{repo_name}]({ssh_url})\n".encode()
        ).decode(),
    }
    response = send_github_request(
        f"/repos/{USERNAME}/SPY-LIST/contents/README.md", "PUT", headers, data
    )

    if response.status_code == 201:
        print(f"Successfully updated SPY-LIST with SPY-{repo_name}")
    else:
        print(f"ERROR: Failed to update SPY-LIST with SPY-{repo_name}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")


def push_to_github(repo_path, ssh_url):
    """
    Push local repository to the newly created GitHub repository.
    """
    print(f"Attempting to push local repository {repo_path} to GitHub...")
    push_command = f"cd {repo_path} && git remote add origin {ssh_url} && git push -u origin master"
    push_status = os.system(push_command)

    if push_status == 0:
        print(f"Successfully pushed {repo_path} to GitHub.")
    else:
        print(f"Failed to push {repo_path} to GitHub.")


def main():
    """
    Main function that handles user arguments and the logic of the script.
    """
    parser = argparse.ArgumentParser(
        description="Upload local git repos to GitHub as private repos."
    )
    parser.add_argument("dir", metavar="dir", type=str, help="the directory to upload")
    args = parser.parse_args()

    dir_path = args.dir

    if not os.path.isdir(dir_path):
        print(f"ERROR: {dir_path} is not a directory")
        sys.exit(1)

    print(f"Starting to process repositories in directory {dir_path}...")

    for repo_name in os.listdir(dir_path):
        repo_path = os.path.join(dir_path, repo_name)
        if os.path.isdir(repo_path) and ".git" in os.listdir(repo_path):
            print(f"\nProcessing repository {repo_name}...")
            ssh_url = create_github_repo(repo_name)
            if ssh_url:
                push_to_github(repo_path, ssh_url)
                update_spy_list(repo_name, ssh_url)

    print("\nProcessing completed. Exiting program.")


if __name__ == "__main__":
    main()
