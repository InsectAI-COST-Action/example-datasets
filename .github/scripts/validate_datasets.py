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
from typing import Any, Callable
import re
from urllib.parse import quote_plus
import os

from frictionless import validate, Report, Error

# ==========================================
# 📐 DATA MODELS & REGISTRY
# ==========================================

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

VALIDATION_RULES: list[Callable[[Path], RuleReturn]] = []

def rule(func: Callable[[Path], RuleReturn]) -> Callable[[Path], RuleReturn | list[RuleReturn]]:
    """Decorator to automatically register a validation rule."""
    VALIDATION_RULES.append(func)
    return func

# ==========================================
# 🛠️ DATASET VALIDATION RULES
# ==========================================

@rule
def check_media_dir(dataset_path: Path) -> RuleReturn:
    status = (dataset_path / "media").is_dir()
    if status:
        msg = 'Successfully found "media" folder!'
    else:
        msg = 'Missing "media" folder.\nThe "media" folder should contain all images, potentially organized into subdirectories.'
    return RuleReturn(status=status, name="Directory: media", message=msg)

@rule
def check_raw_labels_dir(dataset_path: Path) -> RuleReturn:
    status = (dataset_path / "raw-data").is_dir()
    misspellings = ["rawdata", "data", "raw_data", "raw-labels", "raw_labels"]
    if status:
        msg = 'Successfully found "raw-data" folder!'
    else:
        msg = 'Missing "raw-data" folder.'
        for misspelling in misspellings:
            if (dataset_path / misspelling).is_dir():
                msg += f'\nFound incorrect folder "{misspelling}".'
    return RuleReturn(status=status, name="Directory: raw-data", message=msg)

@rule
def check_code_dir(dataset_path: Path) -> RuleReturn:
    status = (dataset_path / "code").is_dir()
    if status:
        msg = 'Successfully found "code" folder!'
    else:
        msg = 'Missing "code" folder.\nThe "code" folder should contain the conversion scripts (Jupyter, R, etc.) used to convert the raw data.'
    return RuleReturn(status=status, name="Directory: code", message=msg)

@rule
def check_readme(dataset_path: Path) -> RuleReturn:
    status = (dataset_path / "README.md").is_file()
    if status:
        msg = 'Successfully found "README.md"!'
    else:
        msg = 'Missing "README.md". The "README.md" should describe the dataset, its source, and details about the conversion.'
    return RuleReturn(status=status, name="File: README.md", message=msg)

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

@rule
def check_datapackage(dataset_path : Path) -> list[RuleReturn]:
    datapackage_path = dataset_path / "datapackage.json"
    if not datapackage_path.exists():
        return [RuleReturn(
            status=False,
            name='File: datapackage.json[missing]',
            message=f'Missing "datapackage.json" file, expected {datapackage_path}'
        )]
    
    result : Report = validate(source=datapackage_path)
    
    task_errors = {
        task.name : [Violation.from_error(error) for error in task.errors]
        for task in result.tasks
    }
    
    ret : list[RuleReturn] = []
    
    for error in result.errors:
        viol = Violation.from_error(error)
        ret.append(RuleReturn(
            status=False,
            name=f'File: datapackage.json[{viol.type}]',
            message=f'**frictionless[{viol.type}]: {viol.title}**\n{viol.message}\nNote: {viol.note}',
            data=viol.to_dict()
        ))
        
    for task, errors in task_errors.items():
        for error in errors:
            error_data = error.to_dict()
            ret.append(RuleReturn(
                status=False,
                name=f'File: datapackage.json[{task}]',
                message=f'**frictionless[{task}]: {error.title}**\n' + '\n'.join(f'{k}: {v}' for k, v in error_data.items()),
                data=error_data
            ))
            
    if ret:
        return ret
    
    return [RuleReturn(
        status=True,
        name="File: datapackage.json[all]",
        message='Dataset specification file "datapackage.json" passed `frictionless` validation.'
    )]

def extract_readme_image(dataset_path: Path) -> str | None:
    """Extracts the image path from the first line of the README if formatted correctly."""
    image_path_embed_pattern = re.compile(r"^\s*<!--\s*Image:\s*(.+)\s*-->\s*$", re.IGNORECASE)
    readme_path = dataset_path / "README.md"
    if not readme_path.exists():
        return None
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            mtch = re.match(image_path_embed_pattern, first_line)
            if not mtch:
                return None
            mtch = mtch.group(1).strip()
            image_path = dataset_path.joinpath(*mtch.split("/"))
            return "/".join(map(quote_plus, str(image_path).strip().split(os.sep)))
    except Exception:
        pass
    return None

# ==========================================
# 🚀 CORE EXECUTION LOGIC   
# ==========================================

def check(datasets_dir: str):
    base_path = Path(datasets_dir)
    if not base_path.exists() or not base_path.is_dir():
        return None

    checks = {}
    
    for dataset_path in base_path.iterdir():
        if not dataset_path.is_dir():
            continue 
        
        items = []
        for run_rule in VALIDATION_RULES:
            result = run_rule(dataset_path)
            if isinstance(result, RuleReturn):
                result = [result]
            for rrt in result:
                items.append(rrt.to_dict())

        checks[dataset_path.name] = {
            "image": extract_readme_image(dataset_path),
            "checks": items
        }
            
    return checks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="datasets")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = check(args.dir)
    
    if checks is None:
        print(f"⚠️  Warning: Directory '{args.dir}' not found.", file=sys.stderr)
        sys.exit(1)

    has_failures = any(not item.get("status", None) for item in checks.get("checks", checks).values())

    if args.format == "json":
        print(json.dumps(checks))
    else:
        for ds, rule_results in checks.items():
            print(f"\nDataset: {ds}")
            for result in rule_results:
                status_str = "Success" if result.get("status", False) else "Failed"
                print(f"   - {status_str}: {result['name']}")
                if result.get("message", None):
                    print(f"     💡 {' '.join(str(result['message']).splitlines())}")
            print()
    
    sys.exit(1 if has_failures else 0)

if __name__ == "__main__":
    main()