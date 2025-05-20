#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup


def list_projects():
    """List all available projects in the generated_projects directory."""
    projects_dir = Path("django-generator/generated_projects")
    if not projects_dir.exists():
        print("No projects directory found!")
        return []

    projects = [d for d in projects_dir.iterdir() if d.is_dir()]
    return sorted(projects)


class TemplateQualityChecker:
    def __init__(self, template_path):
        self.template_path = template_path
        self.results = {}

    def check_inline_styles(self, soup):
        """Check for inline styles"""
        elements_with_inline = soup.find_all(style=True)
        return {
            "count": len(elements_with_inline),
            "elements": [str(el) for el in elements_with_inline],
        }

    def check_accessibility(self, soup):
        """Check for accessibility issues"""
        issues = {
            "missing_alt": [],
            "missing_aria": [],
            "color_contrast": [],
            "form_labels": [],
        }

        # Check images for alt text
        for img in soup.find_all("img"):
            if not img.get("alt"):
                issues["missing_alt"].append(str(img))

        # Check for ARIA labels on interactive elements
        for element in soup.find_all(["button", "input", "select", "textarea"]):
            if not (element.get("aria-label") or element.get("aria-labelledby")):
                issues["missing_aria"].append(str(element))

        # Check for form labels
        for input_field in soup.find_all(["input", "select", "textarea"]):
            input_id = input_field.get("id")
            if input_id:
                label = soup.find("label", {"for": input_id})
                if not label:
                    issues["form_labels"].append(str(input_field))

        # Check for color contrast issues (basic check)
        for element in soup.find_all(style=True):
            style = element["style"]
            if "color:" in style and "background-color:" not in style:
                issues["color_contrast"].append(str(element))

        return issues

    def check_django_template_tags(self, content):
        """Check Django template tag usage and best practices"""
        template_issues = {
            "extends": [],
            "blocks": [],
            "includes": [],
            "url_tags": [],
            "static_tags": [],
            "csrf_tokens": [],
            "form_errors": [],
            "potential_xss": [],
        }

        # Check template inheritance
        extends_pattern = r"{%\s*extends\s+['\"](.+?)['\"]\s*%}"
        template_issues["extends"] = re.findall(extends_pattern, content)

        # Check block usage
        block_pattern = r"{%\s*block\s+(\w+)\s*%}"
        template_issues["blocks"] = re.findall(block_pattern, content)

        # Check includes
        include_pattern = r"{%\s*include\s+['\"](.+?)['\"]\s*%}"
        template_issues["includes"] = re.findall(include_pattern, content)

        # Check URL tags
        url_pattern = r"{%\s*url\s+['\"](.+?)['\"]\s*%}"
        template_issues["url_tags"] = re.findall(url_pattern, content)

        # Check static tags
        static_pattern = r"{%\s*static\s+['\"](.+?)['\"]\s*%}"
        template_issues["static_tags"] = re.findall(static_pattern, content)

        # Check CSRF tokens
        csrf_pattern = r"{%\s*csrf_token\s*%}"
        template_issues["csrf_tokens"] = re.findall(csrf_pattern, content)

        # Check form error handling
        form_errors_pattern = r"{{.*?\.errors.*?}}"
        template_issues["form_errors"] = re.findall(form_errors_pattern, content)

        # Check for potential XSS vulnerabilities
        unsafe_pattern = r"{{.*?\|safe.*?}}"
        template_issues["potential_xss"] = re.findall(unsafe_pattern, content)

        return template_issues

    def check_javascript(self, soup):
        """Check JavaScript code quality and best practices"""
        js_issues = {
            "inline_scripts": [],
            "event_handlers": [],
            "jquery_usage": [],
            "fetch_usage": [],
            "error_handling": [],
        }

        # Check inline scripts
        for script in soup.find_all("script"):
            if not script.get("src"):
                js_issues["inline_scripts"].append(str(script))

        # Check inline event handlers
        for element in soup.find_all(True):
            for attr in element.attrs:
                if attr.startswith("on"):
                    js_issues["event_handlers"].append(f"{element.name}[{attr}]")

        # Check for jQuery usage
        jquery_pattern = r"\$\(|jQuery\("
        for script in soup.find_all("script"):
            if script.string and re.search(jquery_pattern, script.string):
                js_issues["jquery_usage"].append(str(script))

        # Check for fetch API usage
        fetch_pattern = r"fetch\("
        for script in soup.find_all("script"):
            if script.string and re.search(fetch_pattern, script.string):
                js_issues["fetch_usage"].append(str(script))

        # Check for error handling in fetch calls
        for script in soup.find_all("script"):
            if script.string:
                fetch_calls = re.findall(r"fetch\(.*?\)", script.string)
                for call in fetch_calls:
                    if ".catch" not in call and "catch" not in call:
                        js_issues["error_handling"].append(call)

        return js_issues

    def check_structure(self, soup):
        """Check template structure and organization"""
        structure = {
            "block_count": len(soup.find_all("block")),
            "extends_count": len(soup.find_all("extends")),
            "include_count": len(soup.find_all("include")),
            "form_count": len(soup.find_all("form")),
            "script_count": len(soup.find_all("script")),
            "nested_forms": [],
            "form_validation": [],
        }

        # Check for nested forms
        for form in soup.find_all("form"):
            if form.find_parent("form"):
                structure["nested_forms"].append(str(form))

        # Check for client-side form validation
        for form in soup.find_all("form"):
            if not form.find_all(["required", "pattern", "min", "max"]):
                structure["form_validation"].append(str(form))

        return structure

    def analyze_template(self, file_path):
        """Analyze a single template file"""
        with open(file_path, "r") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")

        return {
            "inline_styles": self.check_inline_styles(soup),
            "accessibility": self.check_accessibility(soup),
            "django_template_tags": self.check_django_template_tags(content),
            "javascript": self.check_javascript(soup),
            "structure": self.check_structure(soup),
        }

    def check_all_templates(self):
        """Check all templates in the directory"""
        for root, _, files in os.walk(self.template_path):
            for file in files:
                if file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    self.results[file] = self.analyze_template(file_path)
        return self.results


def ensure_results_dir():
    """Ensure the results directory exists"""
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def check_template_quality(project_path):
    """Run template quality checks for a specific project."""
    print(f"Running template quality checks in {project_path}...")

    # Get project name from path and extract base app name
    project_name = os.path.basename(project_path)
    # Extract base app name by removing the unique identifier (e.g., _10lzj5)
    base_app_name = project_name.split("_")[:-1]
    base_app_name = "_".join(base_app_name)  # Rejoin in case app name has underscores

    template_path = os.path.join(project_path, base_app_name, "templates")

    # Run template quality checks
    checker = TemplateQualityChecker(template_path)
    results = checker.check_all_templates()

    # Calculate metrics
    metrics = {
        "total_templates": len(results),
        "total_issues": 0,
        "accessibility": {
            "missing_alt": 0,
            "missing_aria": 0,
            "color_contrast": 0,
            "form_labels": 0,
        },
        "inline_styles": 0,
        "template_tags": {
            "extends": 0,
            "blocks": 0,
            "includes": 0,
            "url_tags": 0,
            "static_tags": 0,
            "csrf_tokens": 0,
            "form_errors": 0,
            "potential_xss": 0,
        },
        "javascript": {
            "inline_scripts": 0,
            "event_handlers": 0,
            "jquery_usage": 0,
            "fetch_usage": 0,
            "error_handling": 0,
        },
        "structure": {
            "block_count": 0,
            "extends_count": 0,
            "include_count": 0,
            "form_count": 0,
            "script_count": 0,
            "nested_forms": 0,
            "form_validation": 0,
        },
    }

    # Aggregate metrics from all templates
    for template, analysis in results.items():
        # Accessibility issues
        for key in metrics["accessibility"]:
            metrics["accessibility"][key] += len(analysis["accessibility"][key])

        # Inline styles
        metrics["inline_styles"] += analysis["inline_styles"]["count"]

        # Template tags
        for key in metrics["template_tags"]:
            metrics["template_tags"][key] += len(analysis["django_template_tags"][key])

        # JavaScript issues
        for key in metrics["javascript"]:
            metrics["javascript"][key] += len(analysis["javascript"][key])

        # Structure
        for key in metrics["structure"]:
            if key in analysis["structure"]:
                value = analysis["structure"][key]
                if isinstance(value, list):
                    metrics["structure"][key] += len(value)
                else:
                    metrics["structure"][key] += value

    # Calculate total issues
    metrics["total_issues"] = (
        sum(metrics["accessibility"].values())
        + metrics["inline_styles"]
        + sum(metrics["template_tags"].values())
        + sum(metrics["javascript"].values())
        + sum(metrics["structure"].values())
    )

    # Add metadata and metrics to results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_with_metadata = {
        "project": project_name,
        "timestamp": timestamp,
        "metrics": metrics,
        "template_quality": results,
    }

    # Save results
    results_dir = ensure_results_dir()
    output_path = os.path.join(
        results_dir, f"template_quality_{project_name}_{timestamp}.json"
    )
    with open(output_path, "w") as f:
        json.dump(results_with_metadata, f, indent=2)

    print(f"Template quality results saved to {output_path}")

    # Print summary
    print("\nTemplate Quality Metrics:")
    print(f"Total Templates: {metrics['total_templates']}")
    print(f"Total Issues: {metrics['total_issues']}")
    print("\nAccessibility Issues:")
    for key, value in metrics["accessibility"].items():
        print(f"  - {key}: {value}")
    print(f"\nInline Styles: {metrics['inline_styles']}")
    print("\nTemplate Tags:")
    for key, value in metrics["template_tags"].items():
        print(f"  - {key}: {value}")
    print("\nJavaScript Issues:")
    for key, value in metrics["javascript"].items():
        print(f"  - {key}: {value}")
    print("\nStructure:")
    for key, value in metrics["structure"].items():
        print(f"  - {key}: {value}")

    return results_with_metadata


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
        check_template_quality(project_path)
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
                check_template_quality(projects[idx])
                return 0
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a number!")


if __name__ == "__main__":
    sys.exit(main())
