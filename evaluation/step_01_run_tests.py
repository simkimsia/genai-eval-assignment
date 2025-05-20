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


def run_tests(project_path, pytest_args=None):
    """Run tests for a specific project."""
    print(f"Running tests in {project_path}...")

    # Change to project directory
    os.chdir(project_path)

    # Add project directory to Python path
    sys.path.insert(0, os.getcwd())

    # Get project name from path and extract base app name
    project_name = os.path.basename(project_path)
    # Extract base app name by removing the unique identifier (e.g., _10lzj5)
    base_app_name = project_name.split("_")[:-1]
    base_app_name = "_".join(base_app_name)  # Rejoin in case app name has underscores

    # Base pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"{base_app_name}/tests/",  # Use base app name for test directory
        f"--cov={base_app_name}",  # Use base app name for coverage
        "--cov-report=term-missing",
        "-v",  # verbose output
        "--ds=project_placeholder.settings",  # Use correct settings module
        "--reuse-db",  # Reuse test database if it exists
        "--create-db",  # Create test database if it doesn't exist
    ]

    # Add any additional pytest arguments
    if pytest_args:
        pytest_cmd.extend(pytest_args)

    # Run pytest with coverage and database setup
    result = subprocess.run(pytest_cmd)

    # Print coverage report
    print("\nCoverage Report:")
    subprocess.run([sys.executable, "-m", "coverage", "report", "-m"])

    return result.returncode


def main():
    # List available projects
    projects = list_projects()

    if not projects:
        print("No projects found!")
        return 1

    # Parse arguments
    pytest_args = []
    project_path = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--":
            # Everything after -- goes to pytest
            pytest_args = sys.argv[i + 1 :]
            break
        elif not project_path and os.path.exists(sys.argv[i]):
            project_path = sys.argv[i]
        i += 1

    # If project path provided as argument, use it
    if project_path:
        return run_tests(project_path, pytest_args)

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
                return run_tests(projects[idx], pytest_args)
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a number!")


if __name__ == "__main__":
    sys.exit(main())
