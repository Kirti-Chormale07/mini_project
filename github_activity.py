#!/usr/bin/env python3
"""Fetch and print a GitHub user's recent public activity."""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://api.github.com/users/{username}/events"


def repository(event: dict[str, Any]) -> str:
  """Return the repository name when GitHub supplied one."""
  return event.get("repo", {}).get("name", "an unknown repository")


def format_event(event: dict[str, Any]) -> str:
  """Convert one GitHub event payload to a readable line."""
  event_type = event.get("type", "UnknownEvent")
  repo = repository(event)
  payload = event.get("payload", {})

  if event_type == "PushEvent":
    commits = len(payload.get("commits", []))
    return f"Pushed {commits} commit{'s' if commits != 1 else ''} to {repo}"
  if event_type == "IssuesEvent":
    action = payload.get("action", "updated")
    return f"{action.capitalize()} an issue in {repo}"
  if event_type == "IssueCommentEvent":
    return f"Commented on an issue in {repo}"
  if event_type == "PullRequestEvent":
    action = payload.get("action", "updated")
    return f"{action.capitalize()} a pull request in {repo}"
  if event_type == "PullRequestReviewEvent":
    return f"Reviewed a pull request in {repo}"
  if event_type == "WatchEvent":
    return f"Starred {repo}"
  if event_type == "ForkEvent":
    return f"Forked {repo}"
  if event_type == "CreateEvent":
    ref_type = payload.get("ref_type", "repository")
    ref = payload.get("ref")
    return f"Created {ref_type}{' ' + ref if ref else ''} in {repo}"
  if event_type == "DeleteEvent":
    ref_type = payload.get("ref_type", "branch")
    ref = payload.get("ref")
    return f"Deleted {ref_type}{' ' + ref if ref else ''} in {repo}"
  if event_type == "ReleaseEvent":
    return f"Published a release in {repo}"
  if event_type == "PublicEvent":
    return f"Made {repo} public"
  if event_type == "MemberEvent":
    return f"Added a collaborator to {repo}"

    # New GitHub event types can still be displayed without breaking the CLI.
    return f"{event_type.removesuffix('Event')} activity in {repo}"


def fetch_events(username: str) -> list[dict[str, Any]]:
  """Fetch public events for *username* from GitHub's REST API."""
  request = Request(
    API_URL.format(username=username),
    headers={
      "Accept": "application/vnd.github+json",
      "User-Agent": "github-activity-cli",
      "X-GitHub-Api-Version": "2022-11-28",
      },
    )

  try:
    with urlopen(request, timeout=10) as response:
      data = json.load(response)
  except HTTPError as error:
    if error.code == 404:
      raise RuntimeError(f"GitHub user '{username}' was not found.") from error
    if error.code == 403:
      raise RuntimeError("GitHub API rate limit reached. Try again later.") from error
      raise RuntimeError(f"GitHub API returned HTTP {error.code}.") from error
  except URLError as error:
    raise RuntimeError(f"Could not connect to GitHub: {error.reason}") from error
  except TimeoutError as error:
    raise RuntimeError("The request to GitHub timed out. Try again.") from error
  except json.JSONDecodeError as error:
    raise RuntimeError("GitHub returned an invalid response.") from error

    if not isinstance(data, list):
      raise RuntimeError("GitHub returned an unexpected response.")
    return data


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("Usage: python github_activity.py <github-username>")
        return 1

    if arguments[0] in {"-h", "--help"}:
        print("Usage: python github_activity.py <github-username>")
        return 0

    username = arguments[0].strip()
    if not username:
        print("Error: GitHub username cannot be empty.", file=sys.stderr)
        return 1

    try:
        events = fetch_events(username)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if not events:
        print(f"No recent public activity found for {username}.")
        return 0

    print(f"Recent activity for {username}:")
    for event in events:
      print(f"- {format_event(event)}")
    return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
