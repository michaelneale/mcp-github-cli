from mcp.server.fastmcp import FastMCP
import os
import logging
import json
import subprocess
import shlex
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

instructions = """The GitHub MCP server provides focused tools for interacting with GitHub using REST and GraphQL APIs.

Examples:
- Get repository info: `gh_graphql_repo_info("block/goose")`
- Search repositories: `gh_rest_search_repos("language:python stars:>1000")`
- Get user profile: `gh_graphql_user_profile("octocat")`
- List pull requests: `gh_graphql_pull_requests("block/goose", 5)`
- Get repository contents: `gh_rest_repo_contents("block/goose", "README.md")`

Each tool has a clear example in its description to show the exact format for inputs.
"""

mcp = FastMCP("GitHub CLI", instructions=instructions)

# Helper function to run GitHub CLI commands
def run_gh_command(command_args, input_data=None):
    """
    Run a GitHub CLI command and return the result
    
    Args:
        command_args: List of command arguments
        input_data: Optional input data for the command
        
    Returns:
        Dict with command result
    """
    try:
        # Create the full command
        cmd = ["gh"] + command_args
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run the command
        if input_data:
            process = subprocess.run(
                cmd, 
                input=input_data.encode(), 
                capture_output=True, 
                text=True
            )
        else:
            process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check for errors
        if process.returncode != 0:
            error_message = process.stderr.strip() or f"Command failed with exit code {process.returncode}"
            logger.error(f"Command failed: {error_message}")
            return {"success": False, "error": error_message}
        
        # Try to parse JSON output
        output = process.stdout.strip()
        if output and output.startswith(("{", "[")):
            try:
                return {"success": True, "data": json.loads(output)}
            except json.JSONDecodeError:
                # Not valid JSON, return as text
                return {"success": True, "output": output}
        
        # Return text output
        return {"success": True, "output": output}
    
    except Exception as e:
        logger.error(f"Error running GitHub CLI command: {str(e)}")
        return {"success": False, "error": str(e)}

#
# User Information Tools
#

@mcp.tool()
def gh_get_me() -> Dict[str, Any]:
    """
    Get details of the authenticated user.
        
    Returns:
        Information about the authenticated user including login, name, and organizations
    """
    query = '''
    query {
      viewer {
        login
        name
        bio
        company
        location
        websiteUrl
        twitterUsername
        avatarUrl
        organizations(first: 10) {
          nodes {
            login
            name
          }
        }
        repositories(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            name
            description
            url
          }
        }
      }
    }
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

#
# GraphQL API Tools
#

@mcp.tool()
def gh_graphql_repo_info(owner_repo: str) -> Dict[str, Any]:
    """
    Get detailed repository information using GraphQL.
    
    Example: gh_graphql_repo_info("block/goose")
    
    Args:
        owner_repo: Repository in format "owner/repo"
        
    Returns:
        Repository details including stars, forks, issues, PRs, and languages
    """
    owner, repo = owner_repo.split("/")
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        name
        description
        stargazerCount
        forkCount
        url
        createdAt
        updatedAt
        primaryLanguage {{
          name
          color
        }}
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          nodes {{
            name
            color
          }}
        }}
        issues(states: OPEN) {{
          totalCount
        }}
        pullRequests(states: OPEN) {{
          totalCount
        }}
        defaultBranchRef {{
          name
        }}
      }}
    }}
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

@mcp.tool()
def gh_graphql_user_profile(username: str) -> Dict[str, Any]:
    """
    Get detailed user profile information using GraphQL.
    
    Example: gh_graphql_user_profile("octocat")
    
    Args:
        username: GitHub username
        
    Returns:
        User profile details including repositories, contributions, and social info
    """
    query = f'''
    query {{
      user(login: "{username}") {{
        login
        name
        bio
        company
        location
        websiteUrl
        twitterUsername
        url
        avatarUrl
        createdAt
        updatedAt
        followers {{
          totalCount
        }}
        following {{
          totalCount
        }}
        repositories(first: 10, orderBy: {{field: STARGAZERS, direction: DESC}}) {{
          totalCount
          nodes {{
            name
            description
            stargazerCount
            url
          }}
        }}
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
          }}
        }}
      }}
    }}
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

@mcp.tool()
def gh_graphql_pull_requests(owner_repo: str, limit: int = 10, state: str = "OPEN") -> Dict[str, Any]:
    """
    Get pull requests for a repository using GraphQL.
    
    Example: gh_graphql_pull_requests("block/goose", 5)
    
    Args:
        owner_repo: Repository in format "owner/repo"
        limit: Maximum number of PRs to return (default: 10)
        state: PR state (OPEN, CLOSED, MERGED)
        
    Returns:
        Pull request details including title, author, reviewers, and status
    """
    owner, repo = owner_repo.split("/")
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        pullRequests(first: {limit}, states: {state}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            number
            title
            url
            state
            createdAt
            updatedAt
            author {{
              login
              url
            }}
            baseRefName
            headRefName
            isDraft
            mergeable
            reviewDecision
            reviewRequests(first: 10) {{
              nodes {{
                requestedReviewer {{
                  ... on User {{
                    login
                  }}
                }}
              }}
            }}
            reviews(first: 10) {{
              nodes {{
                author {{
                  login
                }}
                state
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

@mcp.tool()
def gh_graphql_issues(owner_repo: str, limit: int = 10, state: str = "OPEN", labels: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get issues for a repository using GraphQL.
    
    Example: gh_graphql_issues("block/goose", 5, "OPEN", ["bug", "help wanted"])
    
    Args:
        owner_repo: Repository in format "owner/repo"
        limit: Maximum number of issues to return (default: 10)
        state: Issue state (OPEN, CLOSED)
        labels: List of labels to filter by
        
    Returns:
        Issue details including title, author, comments, and labels
    """
    owner, repo = owner_repo.split("/")
    
    # Build the labels filter if provided
    labels_filter = ""
    if labels and len(labels) > 0:
        labels_list = ', '.join([f'"{label}"' for label in labels])
        labels_filter = f', labels: [{labels_list}]'
    
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issues(first: {limit}, states: {state}{labels_filter}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            number
            title
            url
            state
            createdAt
            updatedAt
            author {{
              login
              url
            }}
            bodyText
            comments {{
              totalCount
            }}
            labels(first: 10) {{
              nodes {{
                name
                color
              }}
            }}
            assignees(first: 5) {{
              nodes {{
                login
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

@mcp.tool()
def gh_graphql_repo_contributors(owner_repo: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get contributors for a repository using GraphQL.
    
    Example: gh_graphql_repo_contributors("block/goose", 5)
    
    Args:
        owner_repo: Repository in format "owner/repo"
        limit: Maximum number of contributors to return (default: 10)
        
    Returns:
        Contributor details including commit count and recent commits
    """
    owner, repo = owner_repo.split("/")
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        defaultBranchRef {{
          target {{
            ... on Commit {{
              history(first: {limit}) {{
                totalCount
                nodes {{
                  committedDate
                  message
                  author {{
                    name
                    email
                    user {{
                      login
                      url
                    }}
                  }}
                }}
                edges {{
                  node {{
                    author {{
                      user {{
                        login
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    
    return run_gh_command(["api", "graphql", "-f", f"query={query}"])

#
# REST API Tools
#

@mcp.tool()
def gh_rest_search_repos(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for repositories using REST API.
    
    Example: gh_rest_search_repos("language:python stars:>1000", 5)
    
    Args:
        query: Search query
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        Repository search results
    """
    cmd = ["search", "repos", query, "--json", "name,fullName,description,stargazersCount,forksCount,url", "--limit", str(limit)]
    
    return run_gh_command(cmd)

@mcp.tool()
def gh_rest_repo_contents(owner_repo: str, path: str = "", ref: Optional[str] = None) -> Dict[str, Any]:
    """
    Get repository contents using REST API.
    
    Example: gh_rest_repo_contents("block/goose", "README.md")
    
    Args:
        owner_repo: Repository in format "owner/repo"
        path: File or directory path (empty for root)
        ref: Git reference (branch, tag, or commit SHA)
        
    Returns:
        File or directory contents
    """
    cmd = ["api", f"repos/{owner_repo}/contents/{path}"]
    
    if ref:
        cmd.append(f"--ref={ref}")
    
    result = run_gh_command(cmd)
    
    if result["success"] and "data" in result and isinstance(result["data"], dict) and "content" in result["data"]:
        # Try to decode the content if it's base64 encoded
        try:
            import base64
            content = result["data"]["content"]
            result["data"]["decoded_content"] = base64.b64decode(content).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to decode file content: {str(e)}")
    
    return result

@mcp.tool()
def gh_rest_create_issue(owner_repo: str, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create an issue using REST API.
    
    Example: gh_rest_create_issue("your-username/your-repo", "Bug: Login fails", "The login button doesn't work", ["bug", "high-priority"])
    
    Args:
        owner_repo: Repository in format "owner/repo"
        title: Issue title
        body: Issue description
        labels: List of labels to apply
        
    Returns:
        Created issue details
    """
    data = {
        "title": title,
        "body": body
    }
    
    if labels:
        data["labels"] = labels
    
    # Convert to JSON
    json_data = json.dumps(data)
    
    cmd = ["api", f"repos/{owner_repo}/issues", "-X", "POST", "--input", "-"]
    return run_gh_command(cmd, json_data)

@mcp.tool()
def gh_rest_create_pr(owner_repo: str, title: str, body: str, head: str, base: str = "main", draft: bool = False) -> Dict[str, Any]:
    """
    Create a pull request using REST API.
    
    Example: gh_rest_create_pr("your-username/your-repo", "Add login feature", "This PR adds login functionality", "feature-login", "main")
    
    Args:
        owner_repo: Repository in format "owner/repo"
        title: PR title
        body: PR description
        head: Branch containing changes
        base: Branch to merge into (default: main)
        draft: Whether to create as draft PR
        
    Returns:
        Created PR details
    """
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
        "draft": draft
    }
    
    # Convert to JSON
    json_data = json.dumps(data)
    
    cmd = ["api", f"repos/{owner_repo}/pulls", "-X", "POST", "--input", "-"]
    return run_gh_command(cmd, json_data)

@mcp.tool()
def gh_rest_branches(owner_repo: str) -> Dict[str, Any]:
    """
    List branches in a repository using REST API.
    
    Example: gh_rest_branches("block/goose")
    
    Args:
        owner_repo: Repository in format "owner/repo"
        
    Returns:
        List of branches
    """
    cmd = ["api", f"repos/{owner_repo}/branches", "--paginate"]
    return run_gh_command(cmd)

@mcp.tool()
def gh_rest_commits(owner_repo: str, branch: str = "", limit: int = 10) -> Dict[str, Any]:
    """
    List commits in a repository using REST API.
    
    Example: gh_rest_commits("block/goose", "main", 5)
    
    Args:
        owner_repo: Repository in format "owner/repo"
        branch: Branch name (default: default branch)
        limit: Maximum number of commits to return
        
    Returns:
        List of commits
    """
    cmd = ["api", f"repos/{owner_repo}/commits"]
    
    params = []
    if branch:
        params.append(f"sha={branch}")
    
    if limit:
        params.append(f"per_page={limit}")
    
    if params:
        cmd.append("--query=" + "&".join(params))
    
    return run_gh_command(cmd)

@mcp.tool()
def gh_custom_graphql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a custom GraphQL query.
    
    Example: gh_custom_graphql("query { viewer { login name } }")
    
    Args:
        query: GraphQL query
        variables: Optional variables for the query
        
    Returns:
        Query results
    """
    cmd = ["api", "graphql", "-f", f"query={query}"]
    
    if variables:
        for key, value in variables.items():
            if isinstance(value, (str, int, float, bool)):
                cmd.extend(["-f", f"{key}={value}"])
            else:
                # Convert complex types to JSON
                json_value = json.dumps(value)
                cmd.extend(["-f", f"{key}={json_value}"])
    
    return run_gh_command(cmd)

@mcp.tool()
def gh_rest_api(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a custom REST API request.
    
    Example: gh_rest_api("repos/block/goose", "GET", query_params={"sort": "updated"})
    
    Args:
        endpoint: API endpoint (without leading slash)
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        data: Optional request body for POST, PUT, PATCH
        query_params: Optional query parameters
        
    Returns:
        API response
    """
    cmd = ["api", endpoint, "-X", method]
    
    # Add query parameters
    if query_params:
        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
        cmd.append(f"--query={query_string}")
    
    # Add request body if needed
    input_data = None
    if data and method in ["POST", "PUT", "PATCH"]:
        input_data = json.dumps(data)
        cmd.extend(["--input", "-"])
    
    return run_gh_command(cmd, input_data)

def test_github_client():
    """
    Test the GitHub client functionality.
    """
    logger.info("Testing GitHub client...")
    
    try:
        # Test authentication status
        logger.info("Testing authentication status...")
        result = run_gh_command(["auth", "status"])
        
        if result["success"]:
            print("\n=== GitHub Authentication Status ===")
            print(result["output"])
            
            # Test get_me function
            print("\n=== Testing User Information (gh_get_me) ===")
            me_result = gh_get_me()
            if me_result["success"] and "data" in me_result:
                user_data = me_result["data"]["data"]["viewer"]
                print(f"Login: {user_data.get('login', 'N/A')}")
                print(f"Name: {user_data.get('name', 'N/A')}")
                print(f"Company: {user_data.get('company', 'N/A')}")
                print(f"Bio: {user_data.get('bio', 'N/A')}")
                print(f"Location: {user_data.get('location', 'N/A')}")
                
                # Print organizations if available
                orgs = user_data.get('organizations', {}).get('nodes', [])
                if orgs:
                    print("Organizations:")
                    for org in orgs[:3]:  # Show first 3 orgs
                        print(f"  - {org.get('login', 'N/A')}")
                
                # Print recent repositories if available
                repos = user_data.get('repositories', {}).get('nodes', [])
                if repos:
                    print("Recent repositories:")
                    for repo in repos[:3]:  # Show first 3 repos
                        print(f"  - {repo.get('name', 'N/A')}: {repo.get('description', 'No description')}")
            else:
                print(f"Failed to get user information: {me_result.get('error', 'Unknown error')}")
            
            # Test GraphQL query for viewer info
            print("\n=== Testing GraphQL Query - Viewer Info ===")
            graphql_result = gh_custom_graphql("query { viewer { login name } }")
            if graphql_result["success"] and "data" in graphql_result:
                data = graphql_result["data"]["data"]["viewer"]
                print(f"Logged in as: {data.get('login', 'N/A')}")
                print(f"Name: {data.get('name', 'N/A')}")
            else:
                print(f"Failed to execute GraphQL query: {graphql_result.get('error', 'Unknown error')}")
            
            # Test repository search
            print("\n=== Testing Repository Search (REST API) ===")
            repos_result = gh_rest_search_repos("python stars:>1000", 3)
            if repos_result["success"] and "data" in repos_result:
                for repo in repos_result["data"]:
                    print(f"- {repo.get('fullName', 'N/A')}: {repo.get('description', 'No description')}")
                    print(f"  Stars: {repo.get('stargazersCount', 'N/A')}, URL: {repo.get('url', 'N/A')}")
            else:
                print(f"Failed to search repositories: {repos_result.get('error', 'Unknown error')}")
                if 'output' in repos_result:
                    print(f"Output: {repos_result['output']}")
            
            # Test repository info with GraphQL
            print("\n=== Testing Repository Info (GraphQL) ===")
            repo_info = gh_graphql_repo_info("block/goose")
            if repo_info["success"] and "data" in repo_info:
                repo_data = repo_info["data"]["data"]["repository"]
                print(f"Repository: {repo_data.get('name', 'N/A')}")
                print(f"Description: {repo_data.get('description', 'No description')}")
                print(f"Stars: {repo_data.get('stargazerCount', 'N/A')}")
                print(f"Forks: {repo_data.get('forkCount', 'N/A')}")
                print(f"Primary Language: {repo_data.get('primaryLanguage', {}).get('name', 'N/A')}")
                print(f"Open Issues: {repo_data.get('issues', {}).get('totalCount', 'N/A')}")
                print(f"Open PRs: {repo_data.get('pullRequests', {}).get('totalCount', 'N/A')}")
            else:
                print(f"Failed to get repository info: {repo_info.get('error', 'Unknown error')}")
            
            # Test repository branches
            print("\n=== Testing Repository Branches (REST API) ===")
            branches = gh_rest_branches("block/goose")
            if branches["success"] and "data" in branches:
                print(f"Found {len(branches['data'])} branches. First few:")
                for branch in branches["data"][:3]:
                    print(f"- {branch.get('name', 'N/A')}")
            else:
                print(f"Failed to get repository branches: {branches.get('error', 'Unknown error')}")
            
            return True
        else:
            logger.error(f"Failed to authenticate: {result.get('error', 'Unknown error')}")
            print("\n=== GitHub Authentication Failed ===")
            print("Please run 'gh auth login' to authenticate with GitHub")
            return False
            
    except Exception as e:
        logger.error(f"Error testing GitHub client: {str(e)}")
        return False

def main():
    """Entry point for the package when installed via pip."""
    import sys

    # Check if we should run in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_github_client()
    else:
        # Normal MCP server mode
        logger.info("Starting GitHub MCP server...")
        mcp.run()

if __name__ == "__main__":
    main()