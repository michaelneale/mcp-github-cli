# mcp-github-cli

MCP server that wraps the GitHub CLI (`gh`) to provide GitHub functionality for AI agents. This extension enables interaction with GitHub repositories, issues, pull requests, and more through a set of tools that use the GitHub CLI.

## Features

- **User Management**: Get information about the authenticated user
- **Issues**: Create, read, update, and comment on issues
- **Pull Requests**: Create, list, merge, and manage pull requests
- **Repositories**: Create, fork, search, and manage repository content
- **Search**: Search repositories, code, issues, and users

## Prerequisites

1. Install the GitHub CLI (`gh`) if not already installed:
   - macOS: `brew install gh`
   - Linux: `sudo apt install gh`
   - Windows: `winget install GitHub.cli`

2. Authenticate with GitHub:
   ```sh
   gh auth login
   ```

3. Install this package:
   ```sh
   pip install mcp-github-cli
   ```

## Usage

### Running the MCP Server

```sh
mcp-github-cli
```

Or if running from source:

```sh
python main.py
```

### Testing the Client

To test if your GitHub CLI is properly authenticated:

```sh
python main.py --test
```

## Example Tools

Here are some examples of the tools available:

### Issues

- `get_issue(owner_repo, issue_number)`: Get details of an issue
- `create_issue(owner_repo, title, body, assignees, labels)`: Create a new issue
- `add_issue_comment(owner_repo, issue_number, body)`: Add a comment to an issue

### Pull Requests

- `get_pull_request(owner_repo, pull_number)`: Get details of a pull request
- `create_pull_request(owner_repo, title, body, head, base, draft)`: Create a new pull request
- `merge_pull_request(owner_repo, pull_number, merge_method, delete_branch)`: Merge a pull request

### Repositories

- `get_file_contents(owner_repo, path, ref)`: Get contents of a file
- `create_or_update_file(owner_repo, branch, file_path, content, commit_message)`: Create or update a file
- `list_branches(owner_repo)`: List branches in a repository

## Building and Publishing

1. Update version in `pyproject.toml`:

```toml
[project]
version = "x.y.z"  # Update this
```

2. Build the package:

```bash
# Clean previous builds
rm -rf dist/*

# Build in a clean environment
python -m build
```

3. Publish to PyPI:

```bash
python -m twine upload dist/*
```

## License

MIT