Users
get_me - Get details of the authenticated user
No parameters required
Issues
get_issue - Gets the contents of an issue within a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)
get_issue_comments - Get comments for a GitHub issue

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)
create_issue - Create a new issue in a GitHub repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
title: Issue title (string, required)
body: Issue body content (string, optional)
assignees: Usernames to assign to this issue (string[], optional)
labels: Labels to apply to this issue (string[], optional)
add_issue_comment - Add a comment to an issue

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number (number, required)
body: Comment text (string, required)
list_issues - List and filter repository issues

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: Filter by state ('open', 'closed', 'all') (string, optional)
labels: Labels to filter by (string[], optional)
sort: Sort by ('created', 'updated', 'comments') (string, optional)
direction: Sort direction ('asc', 'desc') (string, optional)
since: Filter by date (ISO 8601 timestamp) (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
update_issue - Update an existing issue in a GitHub repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
issue_number: Issue number to update (number, required)
title: New title (string, optional)
body: New description (string, optional)
state: New state ('open' or 'closed') (string, optional)
labels: New labels (string[], optional)
assignees: New assignees (string[], optional)
milestone: New milestone number (number, optional)
search_issues - Search for issues and pull requests

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
Pull Requests
get_pull_request - Get details of a specific pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
list_pull_requests - List and filter repository pull requests

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: PR state (string, optional)
sort: Sort field (string, optional)
direction: Sort direction (string, optional)
perPage: Results per page (number, optional)
page: Page number (number, optional)
merge_pull_request - Merge a pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
commit_title: Title for the merge commit (string, optional)
commit_message: Message for the merge commit (string, optional)
merge_method: Merge method (string, optional)
get_pull_request_files - Get the list of files changed in a pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
get_pull_request_status - Get the combined status of all status checks for a pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
update_pull_request_branch - Update a pull request branch with the latest changes from the base branch

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
expectedHeadSha: The expected SHA of the pull request's HEAD ref (string, optional)
get_pull_request_comments - Get the review comments on a pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
get_pull_request_reviews - Get the reviews on a pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
create_pull_request_review - Create a review on a pull request review

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number (number, required)
body: Review comment text (string, optional)
event: Review action ('APPROVE', 'REQUEST_CHANGES', 'COMMENT') (string, required)
commitId: SHA of commit to review (string, optional)
comments: Line-specific comments array of objects to place comments on pull request changes (array, optional)
For inline comments: provide path, position (or line), and body
For multi-line comments: provide path, start_line, line, optional side/start_side, and body
create_pull_request - Create a new pull request

owner: Repository owner (string, required)
repo: Repository name (string, required)
title: PR title (string, required)
body: PR description (string, optional)
head: Branch containing changes (string, required)
base: Branch to merge into (string, required)
draft: Create as draft PR (boolean, optional)
maintainer_can_modify: Allow maintainer edits (boolean, optional)
add_pull_request_review_comment - Add a review comment to a pull request or reply to an existing comment

owner: Repository owner (string, required)
repo: Repository name (string, required)
pull_number: Pull request number (number, required)
body: The text of the review comment (string, required)
commit_id: The SHA of the commit to comment on (string, required unless using in_reply_to)
path: The relative path to the file that necessitates a comment (string, required unless using in_reply_to)
line: The line of the blob in the pull request diff that the comment applies to (number, optional)
side: The side of the diff to comment on (LEFT or RIGHT) (string, optional)
start_line: For multi-line comments, the first line of the range (number, optional)
start_side: For multi-line comments, the starting side of the diff (LEFT or RIGHT) (string, optional)
subject_type: The level at which the comment is targeted (line or file) (string, optional)
in_reply_to: The ID of the review comment to reply to (number, optional). When specified, only body is required and other parameters are ignored.
update_pull_request - Update an existing pull request in a GitHub repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
pullNumber: Pull request number to update (number, required)
title: New title (string, optional)
body: New description (string, optional)
state: New state ('open' or 'closed') (string, optional)
base: New base branch name (string, optional)
maintainer_can_modify: Allow maintainer edits (boolean, optional)
Repositories
create_or_update_file - Create or update a single file in a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File path (string, required)
message: Commit message (string, required)
content: File content (string, required)
branch: Branch name (string, optional)
sha: File SHA if updating (string, optional)
list_branches - List branches in a GitHub repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
page: Page number (number, optional)
perPage: Results per page (number, optional)
push_files - Push multiple files in a single commit

owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: Branch to push to (string, required)
files: Files to push, each with path and content (array, required)
message: Commit message (string, required)
search_repositories - Search for GitHub repositories

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
create_repository - Create a new GitHub repository

name: Repository name (string, required)
description: Repository description (string, optional)
private: Whether the repository is private (boolean, optional)
autoInit: Auto-initialize with README (boolean, optional)
get_file_contents - Get contents of a file or directory

owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File path (string, required)
ref: Git reference (string, optional)
fork_repository - Fork a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
organization: Target organization name (string, optional)
create_branch - Create a new branch

owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: New branch name (string, required)
sha: SHA to create branch from (string, required)
list_commits - Get a list of commits of a branch in a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Branch name, tag, or commit SHA (string, optional)
path: Only commits containing this file path (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
get_commit - Get details for a commit from a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Commit SHA, branch name, or tag name (string, required)
page: Page number, for files in the commit (number, optional)
perPage: Results per page, for files in the commit (number, optional)
search_code - Search for code across GitHub repositories

query: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
Users
search_users - Search for GitHub users
q: Search query (string, required)
sort: Sort field (string, optional)
order: Sort order (string, optional)
page: Page number (number, optional)
perPage: Results per page (number, optional)
Code Scanning
get_code_scanning_alert - Get a code scanning alert

owner: Repository owner (string, required)
repo: Repository name (string, required)
alertNumber: Alert number (number, required)
list_code_scanning_alerts - List code scanning alerts for a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
ref: Git reference (string, optional)
state: Alert state (string, optional)
severity: Alert severity (string, optional)
tool_name: The name of the tool used for code scanning (string, optional)
Secret Scanning
get_secret_scanning_alert - Get a secret scanning alert

owner: Repository owner (string, required)
repo: Repository name (string, required)
alertNumber: Alert number (number, required)
list_secret_scanning_alerts - List secret scanning alerts for a repository

owner: Repository owner (string, required)
repo: Repository name (string, required)
state: Alert state (string, optional)
secret_type: The secret types to be filtered for in a comma-separated list (string, optional)
resolution: The resolution status (string, optional)
Resources
Repository Content
Get Repository Content Retrieves the content of a repository at a specific path.

Template: repo://{owner}/{repo}/contents{/path*}
Parameters:
owner: Repository owner (string, required)
repo: Repository name (string, required)
path: File or directory path (string, optional)
Get Repository Content for a Specific Branch Retrieves the content of a repository at a specific path for a given branch.

Template: repo://{owner}/{repo}/refs/heads/{branch}/contents{/path*}
Parameters:
owner: Repository owner (string, required)
repo: Repository name (string, required)
branch: Branch name (string, required)
path: File or directory path (string, optional)
Get Repository Content for a Specific Commit Retrieves the content of a repository at a specific path for a given commit.

Template: repo://{owner}/{repo}/sha/{sha}/contents{/path*}
Parameters:
owner: Repository owner (string, required)
repo: Repository name (string, required)
sha: Commit SHA (string, required)
path: File or directory path (string, optional)
Get Repository Content for a Specific Tag Retrieves the content of a repository at a specific path for a given tag.

Template: repo://{owner}/{repo}/refs/tags/{tag}/contents{/path*}
Parameters:
owner: Repository owner (string, required)
repo: Repository name (string, required)
tag: Tag name (string, required)
path: File or directory path (string, optional)
Get Repository Content for a Specific Pull Request Retrieves the content of a repository at a specific path for a given pull request.

Template: repo://{owner}/{repo}/refs/pull/{prNumber}/head/contents{/path*}
Parameters:
owner: Repository owner (string, required)
repo: Repository name (string, required)
prNumber: Pull request number (string, required)
path: File or directory path (string, optional)