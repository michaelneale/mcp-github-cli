# mcp-github-cli

MCP server that provides focused GraphQL and REST API tools for interacting with GitHub. This server offers a streamlined set of powerful tools that leverage GitHub's APIs to provide rich data and functionality.

## Usage

```sh
uvx mcp-github-cli
```

Will run from PyPI. This can be used in `goose` or `claude`.

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

This will run a comprehensive test suite that verifies:
- Authentication status with GitHub
- User information retrieval (gh_get_me)
- GraphQL query functionality (viewer info)
- REST API repository search
- GraphQL repository information retrieval
- REST API branch listing

The test output provides a good demonstration of the capabilities of the different tools.

## Usage from source

### Running from CLI (Goose, or to try it)

```sh
uv --directory /path/to/mcp-github-cli run python main.py
```

## Features

This MCP server focuses on providing powerful, focused tools that leverage GitHub's GraphQL and REST APIs:

### User Information

- `gh_get_me()`: Get detailed information about the authenticated user

### GraphQL Tools

GraphQL tools provide rich, nested data in a single request:

- `gh_graphql_repo_info(owner_repo)`: Get comprehensive repository information
- `gh_graphql_user_profile(username)`: Get detailed user profile data
- `gh_graphql_pull_requests(owner_repo, limit, state)`: Get pull requests with reviewers and status
- `gh_graphql_issues(owner_repo, limit, state, labels)`: Get issues with comments and labels
- `gh_graphql_repo_contributors(owner_repo, limit)`: Get repository contributors and their commits
- `gh_custom_graphql(query, variables)`: Execute a custom GraphQL query

### REST API Tools

REST tools provide specific functionality for common operations:

- `gh_rest_search_repos(query, limit)`: Search for repositories
- `gh_rest_repo_contents(owner_repo, path, ref)`: Get repository contents
- `gh_rest_create_issue(owner_repo, title, body, labels)`: Create an issue
- `gh_rest_create_pr(owner_repo, title, body, head, base, draft)`: Create a pull request
- `gh_rest_branches(owner_repo)`: List repository branches
- `gh_rest_commits(owner_repo, branch, limit)`: List repository commits
- `gh_rest_api(endpoint, method, data, query_params)`: Execute a custom REST API request

## Examples

Here are examples of using these tools:

### User Information

```python
# Get authenticated user information
gh_get_me()
```

### GraphQL Examples

```python
# Get repository information
gh_graphql_repo_info("block/goose")

# Get user profile
gh_graphql_user_profile("octocat")

# Get open pull requests
gh_graphql_pull_requests("block/goose", 5, "OPEN")

# Get issues with specific labels
gh_graphql_issues("block/goose", 10, "OPEN", ["bug", "help wanted"])

# Custom GraphQL query
gh_custom_graphql("""
query {
  viewer {
    login
    name
  }
}
""")
```

### REST API Examples

```python
# Search for repositories
gh_rest_search_repos("language:python stars:>1000", 5)

# Get file contents
gh_rest_repo_contents("block/goose", "README.md")

# Create an issue
gh_rest_create_issue("your-username/your-repo", "Bug report", "There's a bug", ["bug"])

# List branches
gh_rest_branches("block/goose")

# Custom REST API request
gh_rest_api("repos/block/goose", "GET", query_params={"sort": "updated"})
```

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