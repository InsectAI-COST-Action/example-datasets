#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = [
#   "frictionless",
# ]
# ///

import argparse
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Any, Callable, List

from frictionless import validate, Report, Error

# ==========================================
# 📐 DATA MODELS & REGISTRY
# ==========================================

@dataclass
class RuleReturn:
    status: bool
    name: str # What rule is being checked (used for error reporting)
    help: Optional[str] = None
    data: Any = None # Reserved for future serialization of complex errors

    def to_dict(self):
        return {
            "name": self.name,
            "help": self.help,
            "data": self.data
        }

# This list will automatically collect all our decorated rule functions
VALIDATION_RULES: List[Callable[[Path], RuleReturn]] = []

def rule(func: Callable[[Path], RuleReturn]) -> Callable[[Path], RuleReturn | list[RuleReturn]]:
    """Decorator to automatically register a validation rule."""
    VALIDATION_RULES.append(func)
    return func


# ==========================================
# 🛠️ DATASET VALIDATION RULES
# ==========================================

@rule
def check_media_dir(dataset_path: Path) -> RuleReturn:
    return RuleReturn(
        status=(dataset_path / "media").is_dir(),
        name="Directory: media",
        help="Folder containing all images, potentially organized into subdirectories."
    )

@rule
def check_raw_labels_dir(dataset_path: Path) -> RuleReturn:
    return RuleReturn(
        status=(dataset_path / "raw_labels").is_dir(),
        name="Directory: raw_labels",
        help="The original annotations in their source format (JSON, CSV, TXT, etc.)."
    )

@rule
def check_code_dir(dataset_path: Path) -> RuleReturn:
    return RuleReturn(
        status=(dataset_path / "code").is_dir(),
        name="Directory: code",
        help="Folder containing the conversion scripts (Jupyter, R, etc.) used to convert the raw data."
    )

@rule
def check_readme(dataset_path: Path) -> RuleReturn:
    return RuleReturn(
        status=(dataset_path / "README.md").is_file(),
        name="File: README.md",
        help="A readme file describing the dataset, its source, and details about the conversion."
    )


@dataclass
class Violation:
    type : str
    title : str
    description : str
    message : str
    tags : list[str]
    note : str

    @classmethod
    def from_error(cls, error : Error):
        return cls(
            type=error.type,
            title=error.title,
            description=error.description,
            message=error.message,
            tags=error.tags,
            note=error.note
        )
    
    def to_dict(self):
        return {
            "type" : self.type,
            "title" : self.title,
            "description" : self.description,
            "message" : self.message,
            "tag_list" : f'[{",".join(self.tags)}]',
            "note" : self.note
        }
    
    @property
    def markdown(self):
        template = """| {type} | {title} | {description} | {message} | {tag_list} | {note} |"""
        return template.format(**self.to_dict())


def issue_table(violations : list[Violation]) -> str:
    header = "| Type | Title | Description | Message | Tag list | Note |"
    hline = "-"*len(header)
    rows = [violation.markdown for violation in violations]
    return "\n".join([header, hline, *rows, hline])


@rule
def check_datapackage(dataset_path : Path) -> list[RuleReturn]:
    result : Report = validate(source=dataset_path)
    task_errors = {
        task.name : [Violation.from_error(error) for error in task.errors]
        for task in result.tasks
    }
    ret : list[RuleReturn] = []
    for task, errors in task_errors.items():
        for error in errors:
            error_data = error.to_dict()
            ret.append(RuleReturn(
                status=False,
                name=f'frictionless[{task}]: {error.title}',
                help='\n  '.join(f'{k}: {v}' for k, v in error_data.items()),
                data=error_data
            ))
    return ret


# ==========================================
# 🚀 CORE EXECUTION LOGIC   
# ==========================================

def get_violations(datasets_dir: str):
    base_path = Path(datasets_dir)
    if not base_path.exists() or not base_path.is_dir():
        return None, []

    violations = {}
    dataset_names = []
    
    for dataset_path in base_path.iterdir():
        if not dataset_path.is_dir():
            continue 
        
        name = dataset_path.name
        dataset_names.append(name)
        missing_items = []

        # Run every registered rule against this dataset
        for run_rule in VALIDATION_RULES:
            result = run_rule(dataset_path)
            if isinstance(result, RuleReturn):
                result = [result]
            for rrt in result:
                if not rrt.status:
                    missing_items.append(rrt.to_dict())

        violations[name] = missing_items
            
    return violations, dataset_names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="datasets")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    violations, all_datasets = get_violations(args.dir)
    
    if violations is None:
        print(f"⚠️  Warning: Directory '{args.dir}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        # Output JSON payload
        print(json.dumps({"violations": violations, "all_datasets": all_datasets}))
    else:
        for ds, issues in violations.items():
            if not issues:
                print(
                    f"✅ Dataset: {ds}\n"
                    f"   All {len(all_datasets)} datasets passed {len(VALIDATION_RULES)} validation rules.\n"
                )
                continue
            print(f"\n❌ Dataset: {ds}")
            for issue in issues:
                print(f"   - Failed: {issue['name']}")
                if issue.get("help"):
                    print(f"     💡 {"\n        ".join(map(str.strip, issue['help'].splitlines()))}")
            print()
    
    sys.exit(1 if any(violations.values()) else 0)

if __name__ == "__main__":
    main()