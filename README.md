# GitHub User Activity CLI

A dependency-free Python command-line tool that fetches a GitHub user's recent **public** activity and displays it in a readable form.

## Project structure

```text
github-user-activity-use-github-api/
├── github_activity.py  # CLI application
└── README.md           # Setup and usage guide
```

## Requirements

- Python 3.9 or newer
- An internet connection

No packages need to be installed. The program only uses Python's standard library.

## Run it

1. Open a terminal in the project folder.
2. Run the command below, replacing `octocat` with the GitHub username you want to inspect:

   ```powershell
   python github_activity.py octocat
   ```

   On systems where Python is invoked as `python3`, use:

   ```bash
   python3 github_activity.py octocat
   ```

3. Example output:

   ```text
   Recent activity for octocat:
   - Starred owner/example-repository
   - Pushed 2 commits to owner/example-repository
   - Opened an issue in owner/example-repository
   ```

## Help

```powershell
python github_activity.py --help
```

## Error handling

The CLI reports useful messages for missing arguments, nonexistent users, network failures, GitHub API errors, and API rate limits.

## How it works

The application makes a GET request to:

```text
https://api.github.com/users/<username>/events
```

It reads the JSON response and turns common event types (pushes, stars, issues, pull requests, forks, and more) into terminal-friendly messages.
