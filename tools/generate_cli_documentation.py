#!/usr/bin/env python3
"""
Script to generate CLI documentation from the argument parser.
Usage:
    python generate_cli_documentation.py
"""

import sys
from pathlib import Path


def generate_cli_docs():
    # Add the src directory to the path so we can import the modules
    sys.path.insert(0, str(find_project_root() / "src"))
    from pysonar_scanner.configuration.cli import CliConfigurationLoader

    """Generate markdown documentation for CLI arguments."""
    parser = CliConfigurationLoader._CliConfigurationLoader__create_parser()

    # Group arguments by category
    categories = {
        "Authentication": ["token", "sonar_host_url", "sonar_region"],
        "Project Configuration": [
            "sonar_project_key",
            "sonar_project_name",
            "sonar_project_version",
            "sonar_project_description",
            "sonar_project_base_dir",
            "sonar_sources",
            "sonar_tests",
        ],
        "Analysis Configuration": ["verbose", "sonar_python_version", "sonar_filesize_limit"],
        "Report Integration": [
            "sonar_python_coverage_report_paths",
            "sonar_python_pylint_report_path",
            "sonar_sarif_report_paths",
            "sonar_python_xunit_report_path",
            "sonar_python_xunit_skip_details",
            "sonar_python_mypy_report_paths",
            "sonar_python_bandit_report_paths",
            "sonar_python_flake8_report_paths",
            "sonar_python_ruff_report_paths",
            "sonar_external_issues_report_paths",
            "coverage_report_paths",
            "pylint_report_path",
            "xunit_report_path",
            "xunit_skip_details",
            "mypy_report_paths",
            "bandit_report_paths",
            "flake8_report_paths",
            "ruff_report_paths",
        ],
        "Other": [],  # Will contain everything else
    }

    grouped_actions = {category: [] for category in categories}

    # Group actions by category
    for action in parser._actions:
        if action.dest == "help":
            continue

        categorized = False
        for category, dest_prefixes in categories.items():
            for prefix in dest_prefixes:
                if action.dest.startswith(prefix):
                    grouped_actions[category].append(action)
                    categorized = True
                    break
            if categorized:
                break

        if not categorized:
            grouped_actions["Other"].append(action)

    # Generate markdown
    lines = ["# Sonar Scanner Python CLI Arguments", ""]

    for category, actions in grouped_actions.items():
        if not actions:
            continue

        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Option | Description |")
        lines.append("| ------ | ----------- |")

        for action in sorted(actions, key=lambda a: a.option_strings[0] if a.option_strings else ""):
            options = ", ".join(f"`{opt}`" for opt in action.option_strings)
            help_text = action.help or ""
            lines.append(f"| {options} | {help_text} |")

        lines.append("")

    return "\n".join(lines)


def find_project_root():
    """Find the project root by looking for pyproject.toml"""
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            return current_dir
        current_dir = current_dir.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")


if __name__ == "__main__":
    docs = generate_cli_docs()

    project_root = find_project_root()
    output_path = project_root / "CLI_ARGS.md"

    with open(output_path, "w") as f:
        f.write(docs)
