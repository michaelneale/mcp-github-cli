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

logger.info("Starting GitHub MCP server...")

instructions = """The GitHub MCP server allows you to interact with GitHub repositories, issues, pull requests, and more.
It provides a set of tools that wrap the GitHub CLI (gh) to perform common GitHub operations like:

- Managing issues and pull requests
- Working with repositories (creating, forking, listing branches)
- Searching repositories, code, issues, and users
- Managing repository content

To use these tools, you'll need to have the GitHub CLI installed and authenticated.
You can check if you're authenticated by running `gh auth status` in your terminal.
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
        # Commands that don't support --json
        non_json_commands = ["auth", "help", "completion"]
        command_base = command_args[0] if command_args else ""
        
        # Commands that need specific JSON fields
        json_fields_map = {
            "search repos": "name,nameWithOwner,description,stargazerCount,forkCount,url",
            "search issues": "title,url,state,number,repository,createdAt,updatedAt",
            "search code": "repository,path,name,url",
            "search users": "login,name,bio,url,avatarUrl",
            "issue list": "number,title,state,url,createdAt,updatedAt,assignees,labels",
            "pr list": "number,title,state,url,createdAt,updatedAt,headRefName,baseRefName",
            "issue view": "number,title,state,url,body,createdAt,updatedAt,assignees,labels,comments",
            "pr view": "number,title,state,url,body,createdAt,updatedAt,headRefName,baseRefName,mergeable"
        }
        
        # Add --json with appropriate fields if needed
        if "--json" not in " ".join(command_args):
            # Skip for commands that don't support it
            if command_base not in non_json_commands and not (len(command_args) > 1 and command_args[1] == "create" and "--fill" in command_args):
                # Check if we need specific fields
                cmd_key = None
                if len(command_args) >= 2:
                    cmd_key = f"{command_args[0]} {command_args[1]}"
                
                if cmd_key in json_fields_map:
                    command_args.extend(["--json", json_fields_map[cmd_key]])
                else:
                    # Default to just --json for commands that support it
                    command_args.append("--json")
        
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
# User functions
#

@mcp.tool()
def get_me() -> Dict[str, Any]:
    """
    Get details of the authenticated user.
    
    Returns:
        Information about the authenticated user
    """
    return run_gh_command(["auth", "status"])

#
# Issue functions
#

@mcp.tool()
def get_issue(owner_repo: str, issue_number: int) -> Dict[str, Any]:
    """
    Gets the contents of an issue within a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        issue_number: Issue number
        
    Returns:
        Issue details
    """
    return run_gh_command(["issue", "view", str(issue_number), "-R", owner_repo])

@mcp.tool()
def get_issue_comments(owner_repo: str, issue_number: int) -> Dict[str, Any]:
    """
    Get comments for a GitHub issue.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        issue_number: Issue number
        
    Returns:
        List of comments on the issue
    """
    return run_gh_command(["issue", "view", str(issue_number), "-R", owner_repo, "--comments"])

@mcp.tool()
def create_issue(
    owner_repo: str, 
    title: str, 
    body: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new issue in a GitHub repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        title: Issue title
        body: Issue body content
        assignees: Usernames to assign to this issue
        labels: Labels to apply to this issue
        
    Returns:
        Created issue details
    """
    cmd = ["issue", "create", "-R", owner_repo, "--title", title]
    
    if body:
        cmd.extend(["--body", body])
    
    if assignees:
        for assignee in assignees:
            cmd.extend(["--assignee", assignee])
    
    if labels:
        for label in labels:
            cmd.extend(["--label", label])
    
    return run_gh_command(cmd)

@mcp.tool()
def add_issue_comment(owner_repo: str, issue_number: int, body: str) -> Dict[str, Any]:
    """
    Add a comment to an issue.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        issue_number: Issue number
        body: Comment text
        
    Returns:
        Created comment details
    """
    cmd = ["issue", "comment", str(issue_number), "-R", owner_repo, "--body", body]
    return run_gh_command(cmd)

@mcp.tool()
def list_issues(
    owner_repo: str,
    state: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    List and filter repository issues.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        state: Filter by state ('open', 'closed', 'all')
        labels: Labels to filter by
        assignee: Filter by assignee
        limit: Maximum number of issues to fetch
        
    Returns:
        List of issues matching the criteria
    """
    cmd = ["issue", "list", "-R", owner_repo]
    
    if state:
        cmd.extend(["--state", state])
    
    if labels:
        cmd.extend(["--label", ",".join(labels)])
    
    if assignee:
        cmd.extend(["--assignee", assignee])
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

@mcp.tool()
def update_issue(
    owner_repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    add_assignees: Optional[List[str]] = None,
    remove_assignees: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update an existing issue in a GitHub repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        issue_number: Issue number to update
        title: New title
        body: New description
        add_labels: Labels to add
        remove_labels: Labels to remove
        add_assignees: Assignees to add
        remove_assignees: Assignees to remove
        
    Returns:
        Updated issue details
    """
    cmd = ["issue", "edit", str(issue_number), "-R", owner_repo]
    
    if title:
        cmd.extend(["--title", title])
    
    if body:
        cmd.extend(["--body", body])
    
    if add_labels:
        cmd.extend(["--add-label", ",".join(add_labels)])
    
    if remove_labels:
        cmd.extend(["--remove-label", ",".join(remove_labels)])
    
    if add_assignees:
        cmd.extend(["--add-assignee", ",".join(add_assignees)])
    
    if remove_assignees:
        cmd.extend(["--remove-assignee", ",".join(remove_assignees)])
    
    return run_gh_command(cmd)

@mcp.tool()
def search_issues(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for issues and pull requests.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    cmd = ["search", "issues", query]
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

#
# Pull Request functions
#

@mcp.tool()
def get_pull_request(owner_repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get details of a specific pull request.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        pull_number: Pull request number
        
    Returns:
        Pull request details
    """
    return run_gh_command(["pr", "view", str(pull_number), "-R", owner_repo])

@mcp.tool()
def list_pull_requests(
    owner_repo: str,
    state: Optional[str] = None,
    base: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    List and filter repository pull requests.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        state: PR state ('open', 'closed', 'merged', 'all')
        base: Filter by base branch
        limit: Maximum number of PRs to fetch
        
    Returns:
        List of pull requests matching the criteria
    """
    cmd = ["pr", "list", "-R", owner_repo]
    
    if state:
        cmd.extend(["--state", state])
    
    if base:
        cmd.extend(["--base", base])
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

@mcp.tool()
def merge_pull_request(
    owner_repo: str,
    pull_number: int,
    merge_method: Optional[str] = None,
    delete_branch: bool = False
) -> Dict[str, Any]:
    """
    Merge a pull request.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        pull_number: Pull request number
        merge_method: Merge method ('merge', 'squash', or 'rebase')
        delete_branch: Whether to delete the head branch after merging
        
    Returns:
        Merge result
    """
    cmd = ["pr", "merge", str(pull_number), "-R", owner_repo]
    
    if merge_method:
        cmd.append(f"--{merge_method}")
    
    if delete_branch:
        cmd.append("--delete-branch")
    
    return run_gh_command(cmd)

@mcp.tool()
def get_pull_request_files(owner_repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get the list of files changed in a pull request.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        pull_number: Pull request number
        
    Returns:
        List of files changed in the pull request
    """
    return run_gh_command(["pr", "view", str(pull_number), "-R", owner_repo, "--files"])

@mcp.tool()
def create_pull_request(
    owner_repo: str,
    title: Optional[str] = None,
    body: Optional[str] = None,
    head: Optional[str] = None,
    base: Optional[str] = None,
    draft: bool = False,
    fill: bool = False
) -> Dict[str, Any]:
    """
    Create a new pull request.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        title: PR title
        body: PR description
        head: Branch containing changes
        base: Branch to merge into
        draft: Create as draft PR
        fill: Fill title and body from commit (if title/body not provided)
        
    Returns:
        Created pull request details
    """
    cmd = ["pr", "create", "-R", owner_repo]
    
    if title:
        cmd.extend(["--title", title])
    
    if body:
        cmd.extend(["--body", body])
    
    if head:
        cmd.extend(["--head", head])
    
    if base:
        cmd.extend(["--base", base])
    
    if draft:
        cmd.append("--draft")
    
    if fill and not (title and body):
        cmd.append("--fill")
    
    return run_gh_command(cmd)

@mcp.tool()
def add_pull_request_comment(owner_repo: str, pull_number: int, body: str) -> Dict[str, Any]:
    """
    Add a comment to a pull request.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        pull_number: Pull request number
        body: Comment text
        
    Returns:
        Created comment details
    """
    cmd = ["pr", "comment", str(pull_number), "-R", owner_repo, "--body", body]
    return run_gh_command(cmd)

@mcp.tool()
def update_pull_request(
    owner_repo: str,
    pull_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    add_assignees: Optional[List[str]] = None,
    remove_assignees: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update an existing pull request in a GitHub repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        pull_number: Pull request number to update
        title: New title
        body: New description
        add_labels: Labels to add
        remove_labels: Labels to remove
        add_assignees: Assignees to add
        remove_assignees: Assignees to remove
        
    Returns:
        Updated pull request details
    """
    cmd = ["pr", "edit", str(pull_number), "-R", owner_repo]
    
    if title:
        cmd.extend(["--title", title])
    
    if body:
        cmd.extend(["--body", body])
    
    if add_labels:
        cmd.extend(["--add-label", ",".join(add_labels)])
    
    if remove_labels:
        cmd.extend(["--remove-label", ",".join(remove_labels)])
    
    if add_assignees:
        cmd.extend(["--add-assignee", ",".join(add_assignees)])
    
    if remove_assignees:
        cmd.extend(["--remove-assignee", ",".join(remove_assignees)])
    
    return run_gh_command(cmd)

#
# Repository functions
#

@mcp.tool()
def create_or_update_file(
    owner_repo: str,
    branch: str,
    file_path: str,
    content: str,
    commit_message: str
) -> Dict[str, Any]:
    """
    Create or update a file in a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        branch: Branch name
        file_path: Path to the file
        content: File content
        commit_message: Commit message
        
    Returns:
        Result of the operation
    """
    import tempfile
    import os
    
    try:
        # Create a temporary file with the content
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Clone the repository to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            clone_cmd = ["repo", "clone", owner_repo, temp_dir, "--", "-b", branch]
            clone_result = run_gh_command(clone_cmd)
            
            if not clone_result["success"]:
                return clone_result
            
            # Create the directory structure if needed
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Copy the content to the file
            with open(temp_file_path, "r") as src, open(full_path, "w") as dst:
                dst.write(src.read())
            
            # Commit and push the changes
            current_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Add the file
                add_cmd = ["git", "add", file_path]
                subprocess.run(add_cmd, check=True)
                
                # Commit the changes
                commit_cmd = ["git", "commit", "-m", commit_message]
                subprocess.run(commit_cmd, check=True)
                
                # Push the changes
                push_cmd = ["git", "push"]
                subprocess.run(push_cmd, check=True)
                
                return {"success": True, "message": f"File {file_path} created or updated in {owner_repo}:{branch}"}
            finally:
                os.chdir(current_dir)
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@mcp.tool()
def list_branches(owner_repo: str) -> Dict[str, Any]:
    """
    List branches in a GitHub repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        
    Returns:
        List of branches
    """
    # Use the API command since there's no direct gh cli command for listing branches
    cmd = ["api", f"repos/{owner_repo}/branches"]
    return run_gh_command(cmd)

@mcp.tool()
def search_repositories(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for GitHub repositories.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    cmd = ["search", "repos", query]
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

@mcp.tool()
def get_file_contents(owner_repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
    """
    Get contents of a file from a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        path: File path
        ref: Git reference (branch, tag, or commit SHA)
        
    Returns:
        File contents
    """
    cmd = ["api", f"repos/{owner_repo}/contents/{path}"]
    
    if ref:
        cmd.append(f"--ref={ref}")
    
    result = run_gh_command(cmd)
    
    if result["success"] and "data" in result:
        # Try to decode the content if it's base64 encoded
        try:
            import base64
            if isinstance(result["data"], dict) and "content" in result["data"]:
                content = result["data"]["content"]
                result["data"]["decoded_content"] = base64.b64decode(content).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to decode file content: {str(e)}")
    
    return result

@mcp.tool()
def fork_repository(owner_repo: str, clone: bool = False) -> Dict[str, Any]:
    """
    Fork a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        clone: Whether to clone the fork after creating it
        
    Returns:
        Forked repository details
    """
    cmd = ["repo", "fork", owner_repo]
    
    if not clone:
        cmd.append("--clone=false")
    
    return run_gh_command(cmd)

@mcp.tool()
def create_branch(owner_repo: str, branch_name: str, base: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new branch in a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        branch_name: Name for the new branch
        base: Base branch or commit to create from
        
    Returns:
        Result of the operation
    """
    import tempfile
    import os
    
    try:
        # Clone the repository to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            clone_cmd = ["repo", "clone", owner_repo, temp_dir]
            clone_result = run_gh_command(clone_cmd)
            
            if not clone_result["success"]:
                return clone_result
            
            # Create the branch
            current_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Checkout the base branch if specified
                if base:
                    checkout_cmd = ["git", "checkout", base]
                    subprocess.run(checkout_cmd, check=True)
                
                # Create and checkout the new branch
                branch_cmd = ["git", "checkout", "-b", branch_name]
                subprocess.run(branch_cmd, check=True)
                
                # Push the branch
                push_cmd = ["git", "push", "--set-upstream", "origin", branch_name]
                subprocess.run(push_cmd, check=True)
                
                return {"success": True, "message": f"Branch {branch_name} created in {owner_repo}"}
            finally:
                os.chdir(current_dir)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def list_commits(owner_repo: str, branch: Optional[str] = None, limit: Optional[int] = 10) -> Dict[str, Any]:
    """
    List commits in a repository.
    
    Args:
        owner_repo: Repository in format "owner/repo"
        branch: Branch name
        limit: Maximum number of commits to list
        
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
def search_code(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for code across GitHub repositories.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    cmd = ["search", "code", query]
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

@mcp.tool()
def search_users(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for GitHub users.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    cmd = ["search", "users", query]
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    return run_gh_command(cmd)

def test_github_client():
    """
    Test the GitHub client functionality.
    """
    logger.info("Testing GitHub client...")
    
    try:
        # Test authentication status
        logger.info("Testing authentication status...")
        result = get_me()
        
        if result["success"]:
            print("\n=== GitHub Authentication Status ===")
            print(result["output"])
            
            # Test listing repositories
            print("\n=== Testing Repository Search ===")
            repos_result = search_repositories("org:github stars:>10000", limit=5)
            if repos_result["success"] and "data" in repos_result:
                for repo in repos_result["data"]:
                    print(f"- {repo.get('nameWithOwner', 'N/A')}: {repo.get('description', 'No description')}")
                    print(f"  Stars: {repo.get('stargazerCount', 'N/A')}, URL: {repo.get('url', 'N/A')}")
            else:
                print(f"Failed to search repositories: {repos_result.get('error', 'Unknown error')}")
                if 'output' in repos_result:
                    print(f"Output: {repos_result['output']}")
            
            # Test a direct API call
            print("\n=== Testing Direct API Call ===")
            api_result = run_gh_command(["api", "user"])
            if api_result["success"] and "data" in api_result:
                user_data = api_result["data"]
                print(f"Logged in as: {user_data.get('login', 'N/A')}")
                print(f"Name: {user_data.get('name', 'N/A')}")
                print(f"Public repos: {user_data.get('public_repos', 'N/A')}")
            else:
                print(f"Failed to call API: {api_result.get('error', 'Unknown error')}")
            
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