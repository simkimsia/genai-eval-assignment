import argparse
import re  # For modifying settings.py
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Configuration ---
# Default name for the generator script file
DEFAULT_GENERATOR_SCRIPT_NAME = "generate_django_app.py"
# Default name for the temporary Django project
DEFAULT_PROJECT_NAME = "host_project"

# --- Helper Functions ---


def run_command(command, cwd=None, capture_output=True):
    """
    Runs a shell command using subprocess and handles errors.

    Args:
        command (list): The command and its arguments as a list of strings.
        cwd (str or Path, optional): The working directory to run the command in. Defaults to None.
        capture_output (bool): Whether to capture stdout/stderr. Defaults to True.

    Returns:
        subprocess.CompletedProcess: The result object from subprocess.run.

    Raises:
        RuntimeError: If the command fails (non-zero exit code).
    """
    print(f"\nRunning command: {' '.join(command)}" + (f" in {cwd}" if cwd else ""))
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,  # Raise CalledProcessError on non-zero exit code
            text=True,  # Work with strings instead of bytes
            capture_output=capture_output,
            encoding="utf-8",  # Ensure consistent encoding
        )
        if capture_output:
            print("STDOUT:\n" + (result.stdout or " (No stdout)"))
            print("STDERR:\n" + (result.stderr or " (No stderr)"))
        print("Command successful.")
        return result
    except FileNotFoundError:
        print(
            f"Error: Command not found - is '{command[0]}' installed and in your PATH?"
        )
        raise
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        if capture_output:
            print("STDOUT:\n" + (e.stdout or " (No stdout)"))
            print("STDERR:\n" + (e.stderr or " (No stderr)"))
        raise RuntimeError(f"Command failed: {' '.join(command)}") from e
    except Exception as e:
        print(f"An unexpected error occurred while running the command: {e}")
        raise


def add_app_to_settings(settings_path, app_name):
    """
    Adds the generated app name to the INSTALLED_APPS list in settings.py.

    Args:
        settings_path (Path): The path to the settings.py file.
        app_name (str): The name of the app to add.

    Raises:
        FileNotFoundError: If settings.py is not found.
        ValueError: If INSTALLED_APPS list cannot be found or modified.
    """
    print(f"Attempting to add '{app_name}' to INSTALLED_APPS in {settings_path}...")
    if not settings_path.is_file():
        raise FileNotFoundError(f"Settings file not found at {settings_path}")

    try:
        content = settings_path.read_text(encoding="utf-8")

        # Use regex to find the INSTALLED_APPS list and insert the app name
        # This regex looks for "INSTALLED_APPS = [" potentially spanning multiple lines
        # and inserts the new app name before the closing bracket ']'
        pattern = re.compile(
            r"(INSTALLED_APPS\s*=\s*\[\s*.*?)(]", re.DOTALL | re.MULTILINE
        )

        # Format the app name string to be inserted
        app_entry = f"    '{app_name}',\n"  # Add trailing comma and newline

        match = pattern.search(content)
        if not match:
            raise ValueError("Could not find INSTALLED_APPS list in settings.py")

        # Insert the app entry right before the closing bracket
        new_content = pattern.sub(r"\1" + app_entry + r"\2", content, count=1)

        if new_content == content:  # Check if substitution happened
            # Fallback: Try appending if simple insertion failed (e.g., empty list)
            pattern_append = re.compile(
                r"(INSTALLED_APPS\s*=\s*\[\s*)(\])", re.DOTALL | re.MULTILINE
            )
            match_append = pattern_append.search(content)
            if match_append:
                new_content = pattern_append.sub(
                    r"\1" + app_entry + r"\2", content, count=1
                )
            else:
                raise ValueError(
                    "Could not modify INSTALLED_APPS list (complex format?)."
                )

        settings_path.write_text(new_content, encoding="utf-8")
        print(f"Successfully added '{app_name}' to INSTALLED_APPS.")

    except Exception as e:
        print(f"Error modifying settings file {settings_path}: {e}")
        raise ValueError(f"Failed to add app to settings: {e}") from e


# --- Main Orchestration Function ---


def main(args):
    """
    Main function to orchestrate the generation and validation process.
    """
    generator_script_path = Path(args.generator_script).resolve()
    if not generator_script_path.is_file():
        print(f"Error: Generator script not found at {generator_script_path}")
        sys.exit(1)

    # Use a temporary directory for isolation
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        print(f"Created temporary directory: {temp_dir}")

        # --- Step 1: Run the Generator Script ---
        generated_app_name = args.app_name or f"synthetic_{Path(temp_dir).name.lower()}"
        generator_args = [
            sys.executable,  # Use the same python interpreter that runs this script
            str(generator_script_path),
            "--app_name",
            generated_app_name,
        ]
        # Add optional arguments passed to the generator
        if args.num_models:
            generator_args.extend(["--num_models", str(args.num_models)])
        if args.avg_fields:
            generator_args.extend(["--avg_fields", str(args.avg_fields)])
        if args.relation_density is not None:  # Check for None as 0.0 is valid
            generator_args.extend(["--relation_density", str(args.relation_density)])
        if args.domain:
            generator_args.extend(["--domain", args.domain])

        # The generator script creates the app directory *inside* the CWD
        try:
            run_command(generator_args, cwd=temp_dir)
        except RuntimeError:
            print("Error: Failed to generate the Django app.")
            sys.exit(1)

        generated_app_path = temp_dir / generated_app_name
        if not generated_app_path.is_dir():
            print(
                f"Error: Generator script did not create the expected app directory: {generated_app_path}"
            )
            sys.exit(1)
        print(f"Generated app path: {generated_app_path}")

        # --- Step 2: Create Host Django Project ---
        host_project_name = DEFAULT_PROJECT_NAME
        try:
            # Create the project *inside* the temp directory, alongside the app
            run_command(
                ["django-admin", "startproject", host_project_name], cwd=temp_dir
            )
        except RuntimeError:
            print("Error: Failed to create the host Django project.")
            sys.exit(1)

        host_project_path = temp_dir / host_project_name
        manage_py_path = host_project_path / "manage.py"
        settings_py_path = host_project_path / host_project_name / "settings.py"

        if not manage_py_path.is_file():
            print(f"Error: manage.py not found at {manage_py_path}")
            sys.exit(1)
        if not settings_py_path.is_file():
            print(f"Error: settings.py not found at {settings_py_path}")
            sys.exit(1)

        # --- Step 3: Configure settings.py ---
        try:
            # Note: The generated app is already in the temp_dir (where manage.py will run)
            # We just need to add its name to INSTALLED_APPS
            add_app_to_settings(settings_py_path, generated_app_name)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: Failed to configure settings.py: {e}")
            sys.exit(1)

        # --- Step 4: Run Migrations ---
        try:
            print(f"Running makemigrations for app '{generated_app_name}'...")
            run_command(
                [
                    sys.executable,
                    str(manage_py_path),
                    "makemigrations",
                    generated_app_name,
                ],
                cwd=host_project_path,
            )  # Run from the project root

            print("Running migrate...")
            run_command(
                [sys.executable, str(manage_py_path), "migrate"], cwd=host_project_path
            )  # Run from the project root

        except RuntimeError:
            print("Error: Failed during Django migration steps.")
            # Optional: Add more specific error handling or reporting here
            sys.exit(1)

        print("\n--- Automation Complete ---")
        print(
            f"Successfully generated app '{generated_app_name}' and ran initial migrations."
        )
        print(f"Temporary project located at: {host_project_path}")
        print("This directory will be automatically cleaned up upon script exit.")
        # If you want to inspect the files, you could add an input() here
        # input("Press Enter to cleanup and exit...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wrapper script to automate synthetic Django app generation and validation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--generator-script",
        default=DEFAULT_GENERATOR_SCRIPT_NAME,
        help="Path to the Django app generator Python script.",
    )
    parser.add_argument(
        "--app-name",
        default=None,  # Default will be generated dynamically
        help="Name for the generated Django app (passed to generator script).",
    )

    # Add arguments to pass through to the generator script
    parser.add_argument(
        "--num_models", type=int, help="Number of models (for generator)"
    )
    parser.add_argument(
        "--avg_fields", type=int, help="Average fields per model (for generator)"
    )
    parser.add_argument(
        "--relation_density", type=float, help="Relation density (for generator)"
    )
    parser.add_argument(
        "--domain",
        choices=["blog", "inventory", "saas", "generic"],
        help="Domain (for generator)",
    )

    # Example: Add argument to control number of runs
    # parser.add_argument("--runs", type=int, default=1, help="Number of generation cycles to run.")

    parsed_args = parser.parse_args()

    # Basic check for django-admin command
    if not shutil.which("django-admin"):
        print(
            "Error: 'django-admin' command not found. Is Django installed and in your PATH?"
        )
        sys.exit(1)

    main(parsed_args)
