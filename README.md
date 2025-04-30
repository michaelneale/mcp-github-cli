# mcp-github-cli

MCP server to give ability to interact with GitHub through the GitHub CLI (`gh`). Provides tools for working with repositories, issues, pull requests, and more. This is conceptually ported over from the official github MCP server - the official one uses personal access tokens which is not ideal in most situations where you can have oauth or github cli available.

## Usage

```sh
uvx mcp-github-cli
```

Will run from pypi. This can be used in `goose` or `claude`.

## Prerequisites

1. Install the GitHub CLI (`gh`) if not already installed:
   - macOS: `brew install gh`
   - Linux: `sudo apt install gh`
   - Windows: `winget install GitHub.cli`

2. Authenticate with GitHub:
   ```sh
   gh auth login
   ```

## Test

```sh
uv run python main.py --test
```

## Usage from source

### Running from cli (Goose, or to try it)

```sh
uv --directory /path/to/mcp-github-cli run python main.py
```

## Features

- **User Management**: Get information about the authenticated user
- **Issues**: Create, read, update, and comment on issues
- **Pull Requests**: Create, list, merge, and manage pull requests
- **Repositories**: Create, fork, search, and manage repository content
- **Search**: Search repositories, code, issues, and users

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

# Or build in a clean environment using uv
uv venv .venv
source .venv/bin/activate
uv pip install build
python -m build
```

3. Publish to PyPI:

```bash
# Install twine if needed
uv pip install twine

# Upload to PyPI
python -m twine upload dist/*
```

## License

MIT