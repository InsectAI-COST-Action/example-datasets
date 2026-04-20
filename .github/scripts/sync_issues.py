#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13,<3.14"
# ///

import os
import json
import subprocess
import argparse
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
    
    @property
    def markdown(self):
        return f'| {"🟢" if self.status else "❌"} | **{self.name}** | {self.message.replace("\n", "<br>")} |'

def rule_check_table(checks : list[RuleReturn]) -> str:
    header = "| Status | Name | Details |"
    hline = "|---|---|---|"
    rows = [check.markdown for check in checks]
    return "\n".join([header, hline, *rows])

def get_issue_number(title):
    """Fetches open issues and strictly matches the title in Python to avoid gh search syntax bugs."""
    cmd = [
        "gh", "issue", "list", 
        "--state", "open", 
        "--limit", "10000",
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
    for ds_name, checks_data in data.items():
        title = f"[Dataset Standard Violation] {ds_name}"
        issue_number = get_issue_number(title) if not dry_run else f'LOCAL[{ds_name}]'
        
        all_checks = [RuleReturn(**check_data) for check_data in checks_data]
        failed_checks = [c for c in all_checks if not c.status]

        # 1. Process Violations (Create or Update)
        if failed_checks:
            table = rule_check_table(all_checks)
            body = f"# Example data check\n\nResults from comparing the structure of datasets/{ds_name}.\n\n{table}"

            if dry_run:
                print(f"\n{'='*50}\nDRY RUN: {'UPDATE' if issue_number else 'CREATE'} ISSUE\n{'='*50}")
                print(f"TITLE: {title}\nBODY:\n{body}")
            else:
                if issue_number:
                    print(f"Updating existing issue #{issue_number} for {ds_name}")
                    subprocess.run(["gh", "issue", "edit", issue_number, "--body", body], check=True)
                else:
                    print(f"Creating new issue for {ds_name}")
                    subprocess.run(["gh", "issue", "create", "--title", title, "--body", body, "--label", "data-standard"], check=True)

        # 2. Process Fixed Datasets (Close Resolved)
        elif not failed_checks and issue_number:
            if dry_run:
                print(f"\n{'='*50}\nDRY RUN: CLOSE ISSUE\n{'='*50}")
                print(f"Closing resolved issue #{issue_number} for {ds_name}")
            else:
                print(f"Closing resolved issue #{issue_number} for {ds_name}")
                subprocess.run([
                    "gh", "issue", "close", issue_number, 
                    "--comment", "✅ All required standard files and directories are now present. Closing issue."
                ], check=True)

def handle_pr(data, dry_run):
    """Handles posting a single formatted comment to the active Pull Request."""
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number and not dry_run:
        print("No PR_NUMBER found in environment.")
        return

    comments = []
    for ds_name, checks_data in data.items():
        all_checks = [RuleReturn(**check_data) for check_data in checks_data]
        if not all_checks:
            continue
            
        table = rule_check_table(all_checks)
        body = f"### Example data check: {ds_name}\n\nResults from comparing the structure of datasets/{ds_name}.\n\n{table}"
        comments.append(body)

    if not comments:
        full_body = "✅ No datasets found to validate."
    else:
        full_body = "\n\n---\n\n".join(comments)

    if dry_run:
        print(f"\n{'='*50}\nDRY RUN: PR COMMENT\n{'='*50}")
        print(f"PR_NUMBER: {pr_number}\nBODY:\n{full_body}")
    else:
        print(f"Commenting on PR #{pr_number}")
        with open("pr_comment_body.md", "w") as f:
            f.write(full_body)
        subprocess.run(["gh", "pr", "comment", pr_number, "--body-file", "pr_comment_body.md"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Sync dataset validation results to GitHub Issues or PRs.")
    parser.add_argument("--mode", choices=["issues", "pr"], default="issues", help="Run mode: sync to issues or comment on PR.")
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

    if args.mode == "pr":
        handle_pr(data, args.dry_run)
    else:
        handle_issues(data, args.dry_run)

if __name__ == "__main__":
    main()