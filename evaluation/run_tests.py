"""
Simple script to run pytest with coverage for the law firm docs project.
"""

import os
import subprocess
import sys
from pathlib import Path

def list_projects():
    """List all available projects in the generated_projects directory."""
    projects_dir = Path("django-generator/generated_projects")
    if not projects_dir.exists():
        print("No projects directory found!")
        return []

    projects = [d for d in projects_dir.iterdir() if d.is_dir()]
    return sorted(projects)

def run_tests(project_path):
    """Run tests for a specific project."""
    print(f"Running tests in {project_path}...")

    # Change to project directory
    os.chdir(project_path)

    # Add project directory to Python path
    sys.path.insert(0, os.getcwd())

    # Run pytest with coverage
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "law_firm_docs/tests/",
        "--cov=law_firm_docs",
        "--cov-report=term-missing",
        "-v",  # verbose output
        "--ds=law_firm_docs.settings"  # explicitly set Django settings module
    ])

    # Print coverage report
    print("\nCoverage Report:")
    subprocess.run([
        sys.executable, "-m", "coverage", "report", "-m"
    ])

    return result.returncode

def main():
    # List available projects
    projects = list_projects()

    if not projects:
        print("No projects found!")
        return 1

    # If project path provided as argument, use it
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        if not os.path.exists(project_path):
            print(f"Project path {project_path} does not exist!")
            return 1
        return run_tests(project_path)

    # Otherwise, show interactive selection
    print("\nAvailable projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project.name}")

    while True:
        try:
            choice = input("\nSelect project number (or 'q' to quit): ")
            if choice.lower() == 'q':
                return 0

            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                return run_tests(projects[idx])
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a number!")

if __name__ == "__main__":
    sys.exit(main())