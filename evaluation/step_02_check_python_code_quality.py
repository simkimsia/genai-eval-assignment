#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def list_projects():
    """List all available projects in the generated_projects directory."""
    projects_dir = Path("django-generator/generated_projects")
    if not projects_dir.exists():
        print("No projects directory found!")
        return []

    projects = [d for d in projects_dir.iterdir() if d.is_dir()]
    return sorted(projects)


def ensure_results_dir():
    """Ensure the results directory exists"""
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def run_pylint(project_path):
    """Run pylint and return the score and issues"""
    try:
        result = subprocess.run(
            ["pylint", project_path], capture_output=True, text=True
        )
        # Extract score from pylint output
        score_match = re.search(
            r"Your code has been rated at ([-+]?\d*\.\d+)/10", result.stdout
        )
        if score_match:
            score = float(score_match.group(1))
        else:
            score = 0.0

        # Extract issues
        issues = []
        for line in result.stdout.split("\n"):
            if ":" in line and ":" in line.split(":", 1)[1]:
                issues.append(line.strip())

        return {"score": score, "issues": issues}
    except Exception as e:
        print(f"Error running pylint: {e}")
        return {"score": 0.0, "issues": [str(e)]}


def run_coverage(project_path):
    """Run coverage and return the percentage and details"""
    try:
        # Check for coverage data
        coverage_file = os.path.join(project_path, ".coverage")
        if not os.path.exists(coverage_file):
            return {
                "percentage": 0,
                "details": [],
                "status": "no_coverage_data",
                "message": "No coverage data found. Run step_01_run_tests.py first to generate coverage data.",
            }

        # Get detailed coverage report
        details_result = subprocess.run(
            ["coverage", "report", "-m"],  # -m flag shows missing lines
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract file-by-file coverage and calculate total
        coverage_details = []
        total_statements = 0
        total_missing = 0

        for line in details_result.stdout.split("\n"):
            if "%" in line and not line.startswith("TOTAL"):
                parts = line.split()
                if len(parts) >= 4:
                    statements = int(parts[1])
                    missing = int(parts[2])
                    coverage = int(parts[3].rstrip("%"))

                    total_statements += statements
                    total_missing += missing

                    coverage_details.append(
                        {
                            "file": parts[0],
                            "statements": statements,
                            "missing": missing,
                            "coverage": coverage,
                        }
                    )

        # Calculate overall percentage
        overall_percentage = 0
        if total_statements > 0:
            overall_percentage = int(
                ((total_statements - total_missing) / total_statements) * 100
            )

        return {
            "percentage": overall_percentage,
            "details": coverage_details,
            "status": "success",
            "message": "Coverage data found and analyzed",
        }
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage command: {e}")
        return {
            "percentage": 0,
            "details": [],
            "status": "error",
            "message": f"Coverage command failed: {e.stderr.decode() if e.stderr else str(e)}",
        }
    except Exception as e:
        print(f"Error running coverage: {e}")
        return {"percentage": 0, "details": [], "status": "error", "message": str(e)}


def analyze_template_complexity(project_path):
    """Analyze HTML template complexity"""
    template_path = os.path.join(project_path, "law_firm_docs", "templates")
    complexity_scores = []

    for root, _, files in os.walk(template_path):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    # Calculate complexity based on:
                    # 1. Number of template tags
                    template_tags = len(re.findall(r"{%|{{|}}", content))
                    # 2. Number of nested blocks
                    nested_blocks = len(re.findall(r"{%\s*block\s+.*?%}", content))
                    # 3. Number of includes
                    includes = len(re.findall(r"{%\s*include\s+.*?%}", content))

                    complexity = template_tags + (nested_blocks * 2) + includes
                    complexity_scores.append({"file": file, "complexity": complexity})

    return complexity_scores


def check_code_quality(project_path):
    """Run code quality checks for a specific project."""
    print(f"Running code quality checks in {project_path}...")

    # Get project name from path
    project_name = os.path.basename(project_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Run checks
    pylint_results = run_pylint(project_path)
    coverage_results = run_coverage(project_path)

    # Prepare results
    results = {
        "project": project_name,
        "timestamp": timestamp,
        "code_quality": {"pylint": pylint_results, "coverage": coverage_results},
    }

    # Save results
    results_dir = ensure_results_dir()
    output_path = os.path.join(
        results_dir, f"code_quality_{project_name}_{timestamp}.json"
    )
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_path}")
    print(f"Pylint Score: {pylint_results['score']}/10")

    # Print coverage information
    if coverage_results["status"] == "no_coverage_data":
        print("\nCoverage: No coverage data found")
        print("Please run step_01_run_tests.py first to generate coverage data")
    else:
        print(f"Coverage: {coverage_results['percentage']}%")
        if coverage_results["status"] == "error":
            print(f"Coverage Error: {coverage_results['message']}")

    # Print summary of issues
    if pylint_results["issues"]:
        print("\nPylint Issues:")
        for issue in pylint_results["issues"][:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(pylint_results["issues"]) > 5:
            print(f"  ... and {len(pylint_results['issues']) - 5} more issues")

    return results


def main():
    # List available projects
    projects = list_projects()

    if not projects:
        print("No projects found!")
        return 1

    # Parse arguments
    project_path = None

    i = 1
    while i < len(sys.argv):
        if os.path.exists(sys.argv[i]):
            project_path = sys.argv[i]
            break
        i += 1

    # If project path provided as argument, use it
    if project_path:
        check_code_quality(project_path)
        return 0

    # Otherwise, show interactive selection
    print("\nAvailable projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project.name}")

    while True:
        try:
            choice = input("\nSelect project number (or 'q' to quit): ")
            if choice.lower() == "q":
                return 0

            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                check_code_quality(projects[idx])
                return 0
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a number!")


if __name__ == "__main__":
    sys.exit(main())
