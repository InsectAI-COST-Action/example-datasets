#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13,<3.14"
# ///

import os
import json
import subprocess
import argparse
import datetime
import re
from typing import Any
from dataclasses import dataclass

@dataclass
class RuleReturn:
    status: bool
    name: str 
    message: str
    data: Any = None 

    def to_dict(self):
        return {
            "status" : self.status,
            "name": self.name,
            "message": self.message,
            "data": self.data
        }
    
    def __bool__(self):
        return self.status
    
    @property
    def markdown(self):
        return f'| {"🟢" if self.status else "❌"} | **{self.name}** | {self.message.replace("\n", "<br>")} |'

def rule_check_table(checks : list[RuleReturn]) -> str:
    header = "| Status | Name | Details |"
    hline = "|---|---|---|"
    rows = [check.markdown for check in checks]
    return "\n".join([header, hline, *rows])


STATUS_SYMBOLS = {
    "failed" : "🔴",
    "partial" : "🟠",
    "almost" : "🟡",
    "success" : "🟢",
    "unknown" : "⚪"
}

def generate_overview_table(data: dict, pr : bool) -> str:
    """Generates a high-level summary table of all datasets and their statuses."""
    em_space = "&emsp;"
    lines = [
        f'| <br>**Dataset**<br> {em_space*15} | <br>**Status**<br>{em_space*9} | <br>**Example Image**<br>{em_space*23} |',
        '| ---: | :---: | :---: |'
    ]
    
    for ds_name, ds_info in sorted(data.items(), key=lambda kv : kv[0]):
        checks = [RuleReturn(**c) for c in ds_info.get("checks", [])]
        
        n_chk = len(checks)
        n_pass = sum(map(bool, checks))
        if n_chk == 0:
            status = "unknown"
        elif n_pass == n_chk:
            status = "success"
        elif n_pass <= 1:
            status = "failed"
        elif (n_pass > n_chk / 2):
            status = "almost"
        else:
            status = "partial"
        status_icon = STATUS_SYMBOLS[status]
        
        img_path = ds_info.get("image")
        # Center tags aren't needed here because the <td> is center-aligned
        img_md = f'<img src="{"./../../blob/main" if pr else ""}{img_path}" height="150">' if img_path else "_No image tag found_"

        lines.append(f"| [**{ds_name}**](/datasets/{ds_name}) | {status_icon} {status.capitalize()} ({n_pass}/{n_chk}) | {img_md} |")
    
    return "\n".join(lines)

def get_repo_flag():
    """Returns the repo flag for gh CLI if running inside GitHub Actions."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    return ["--repo", repo] if repo else []

def get_issue_number(title):
    """Fetches open issues and strictly matches the title in Python."""
    cmd = [
        "gh", "issue", "list", 
        *get_repo_flag(),
        "--state", "open", 
        "--limit", "100",
        "--json", "title,number"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout.strip():
        issues = json.loads(result.stdout)
        for issue in issues:
            if issue.get("title") == title:
                return str(issue.get("number"))
    return ""

def handle_issues(data, dry_run):
    """Handles creating or updating GitHub issues based on dataset violations."""
    repo_flag = get_repo_flag()
    
    for ds_name, ds_info in data.items():
        title = f"[Dataset Standard Violation] {ds_name}"
        issue_number = get_issue_number(title) if not dry_run else f'LOCAL[{ds_name}]'
        
        all_checks = [RuleReturn(**c) for c in ds_info.get("checks", [])]
        failed_checks = [c for c in all_checks if not c.status]

        # 1. Process Violations (Create or Update)
        if failed_checks:
            table = rule_check_table(all_checks)
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            body = f"# Example data check\n\nResults from comparing the structure of datasets/{ds_name}.\n\n{table}\n\n---\n*Last updated: {timestamp}*"

            if dry_run:
                print(f"\n{'='*50}\nDRY RUN: {'UPDATE' if issue_number else 'CREATE'} ISSUE\n{'='*50}")
                print(f"TITLE: {title}\nBODY:\n{body}")
            else:
                if issue_number:
                    print(f"Updating existing issue #{issue_number} for {ds_name}")
                    subprocess.run(["gh", "issue", "edit", issue_number, *repo_flag, "--body", body], check=True)
                else:
                    print(f"Creating new issue for {ds_name}")
                    subprocess.run(["gh", "issue", "create", *repo_flag, "--title", title, "--body", body, "--label", "data-standard"], check=True)

        # 2. Process Fixed Datasets (Close Resolved)
        elif not failed_checks and issue_number:
            if dry_run:
                print(f"\n{'='*50}\nDRY RUN: CLOSE ISSUE\n{'='*50}")
                print(f"Closing resolved issue #{issue_number} for {ds_name}")
            else:
                print(f"Closing resolved issue #{issue_number} for {ds_name}")
                subprocess.run([
                    "gh", "issue", "close", issue_number, 
                    *repo_flag,
                    "--comment", "✅ All required standard files and directories are now present. Closing issue."
                ], check=True)

def handle_pr(data, dry_run):
    """Handles posting or updating a single formatted comment on the active Pull Request."""
    pr_number = os.environ.get("PR_NUMBER")
    
    if not pr_number and not dry_run:
        print("No PR_NUMBER found in environment.")
        return

    repo_flag = get_repo_flag()
    signature = "<!---9a6162c9-b5ed-41a2-8b78-c54e9ffc8f19--->"

    if not data:
        full_body = f"{signature}\n❌❌❌ No datasets found to validate. ❌❌❌"
    else:
        overview = generate_overview_table(data, pr=True)
        comments = [f"{signature}\n## 📊 Dataset Validation Overview\n\n{overview}"]
        
        for ds_name, ds_info in data.items():
            all_checks = [RuleReturn(**c) for c in ds_info.get("checks", [])]
            if not all_checks:
                continue
                
            table = rule_check_table(all_checks)
            body = f"### {ds_name} Breakdown\n\n{table}"
            comments.append(body)

        full_body = "\n\n---\n\n".join(comments)

    if dry_run:
        print(f"\n{'='*50}\nDRY RUN: PR COMMENT\n{'='*50}")
        print(f"PR_NUMBER: {pr_number}\nBODY:\n{full_body}")
    else:
        with open("pr_comment_body.md", "w") as f:
            f.write(full_body)

        assert len(repo_flag) == 2, f'Missing GITHUB_REPOSITORY in environment: {repo_flag=}'

        # Check if we have already commented on this PR by looking for the signature
        cmd_find = ["gh", "api", f"repos/{repo_flag[1]}/issues/{pr_number}/comments"]
        res = subprocess.run(cmd_find, capture_output=True, text=True)
        
        target_comment_id = None
        if res.returncode == 0:
            try:
                existing_comments = json.loads(res.stdout)
                for c in existing_comments:
                    if signature in c.get("body", ""):
                        target_comment_id = c["id"]
                        break
            except json.JSONDecodeError:
                pass

        if target_comment_id:
            print(f"Updating existing comment {target_comment_id} on PR #{pr_number}")
            # Use the GitHub API to PATCH (update) the existing comment
            subprocess.run(["gh", "api", "-X", "PATCH", f"repos/{repo_flag[1]}/issues/comments/{target_comment_id}", "-F", "body=@pr_comment_body.md"], check=True)
        else:
            print(f"Commenting on PR #{pr_number} for the first time")
            # Create a brand new comment
            subprocess.run(["gh", "pr", "comment", pr_number, *repo_flag, "--body-file", "pr_comment_body.md"], check=True)

def handle_readme(data, dry_run):
    """Updates the README.md file with the latest dataset overview table."""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print(f"⚠️ Warning: {readme_path} not found.")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    table = generate_overview_table(data, pr=False)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    # 1. Update Table Block using exact string splitting (safer than regex for markdown tables)
    start_marker = "<!-- START: DATASET PROGRESS TABLE -->"
    start_notice = "<!-- Do NOT manually edit! -->"
    end_timestamp = f"<!-- Last updated: {timestamp} -->"
    end_marker = "<!-- END: DATASET PROGRESS TABLE -->"
    
    if start_marker in content and end_marker in content:
        pre_table = content.split(start_marker)[0].rstrip()
        post_table = content.split(end_marker)[1].lstrip()
        content = "\n".join([
                pre_table,
                start_marker,
                start_notice,
                "",
                table,
                "",
                end_timestamp,
                end_marker,
                post_table
        ])
    else:
        print(f"⚠️ Warning: Could not find table markers in {readme_path}.")

    if dry_run:
        print(f"\n{'='*50}\nDRY RUN: README UPDATE\n{'='*50}")
        print(content)
    else:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ README.md updated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Sync dataset validation results to GitHub Issues or PRs.")
    parser.add_argument("--mode", choices=["issues", "pr", "readme"], default="issues", help="Run mode: sync to issues or comment on PR.")
    parser.add_argument("--dry-run", action="store_true", help="Print the issue/comment content to console instead of pushing to GitHub.")
    parser.add_argument("--test-file", type=str, help="Path to a local JSON file to use instead of the RESULTS env var.")
    args = parser.parse_args()

    if args.test_file:
        with open(args.test_file, 'r') as f:
            data = json.load(f)
    else:
        results_json = os.environ.get("RESULTS", "{}")
        if not results_json:
            print("No RESULTS found in environment and no --test-file provided.")
            return
        data = json.loads(results_json)

    for k, v in data.items():
        if isinstance(v, list):
            data[k] = {"image": None, "checks": v}

    match args.mode:
        case "pr":
            handle_pr(data, args.dry_run)
        case "issues":
            handle_issues(data, args.dry_run)
        case "readme":
            handle_readme(data, args.dry_run)

if __name__ == "__main__":
    main()