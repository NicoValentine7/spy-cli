#!/usr/bin/env python3
import os
import sys
import argparse
import requests
import base64
import git
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


def push_to_github(repo_path, github_url):
    # リポジトリを取得
    repo = git.Repo(repo_path)

    # リモート名を定義
    remote_name = "temp_remote"

    # リモートがすでに存在するか確認し、存在しなければ追加
    if remote_name not in [remote.name for remote in repo.remotes]:
        repo.create_remote(remote_name, url=github_url)

    try:
        # GitHubへプッシュ
        repo.git.push(remote_name, "HEAD:master")
        print(f"Successfully pushed {repo_path} to GitHub.")
    except git.GitCommandError as error:
        print(f"Failed to push {repo_path} to GitHub. Error: {error}")


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
        # If the directory itself is a git repository
        if ".git" in os.listdir(dir_path):
            print(f"\nProcessing repository {dir_path}...")
            ssh_url = create_github_repo(dir_path)
            if ssh_url:
                push_to_github(dir_path, ssh_url)
                update_spy_list(dir_path, ssh_url)
            break
        # If the sub-directory is a git repository
        elif os.path.isdir(repo_path) and ".git" in os.listdir(repo_path):
            print(f"\nProcessing repository {repo_name}...")
            ssh_url = create_github_repo(repo_name)
            if ssh_url:
                push_to_github(repo_path, ssh_url)
                update_spy_list(repo_name, ssh_url)
    print("\nProcessing completed. Exiting program.")


if __name__ == "__main__":
    main()
