import argparse
import os
import random
import shutil

# from random import poissonvariate # Removed as it causes ImportError
import string
import sys
from pathlib import Path  # Added for path manipulation

import numpy as np  # Added numpy import


# --- Helper Functions ---
def generate_random_suffix(length=4):
    """Generates a short random alphanumeric suffix."""
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_unique_project_name(base_dir=".."):
    """Generates a unique directory name for the project relative to base_dir."""
    base_path = Path(base_dir).resolve()
    attempts = 0
    while attempts < 100:  # Avoid infinite loop
        name = f"synthetic_project_{generate_random_suffix(6)}"
        path = base_path / name
        if not path.exists():
            return name
        attempts += 1
    raise RuntimeError("Could not generate a unique project name after 100 attempts.")


# --- Domain-Specific Naming ---

# Simple word lists for generating names based on domain
DOMAIN_WORDS = {
    "blog": {
        "nouns": [
            "Post",
            "Article",
            "Comment",
            "Category",
            "Tag",
            "Author",
            "User",
            "Entry",
            "Publication",
        ],
        "fields": [
            "title",
            "content",
            "body",
            "pub_date",
            "updated_at",
            "status",
            "slug",
            "excerpt",
            "author",
            "category",
            "tags",
            "name",
            "email",
            "website",
            "text",
            "created_on",
            "active",
            "view_count",
        ],
    },
    "inventory": {
        "nouns": [
            "Product",
            "Item",
            "Stock",
            "Warehouse",
            "Supplier",
            "Order",
            "Customer",
            "Shipment",
            "Location",
            "Category",
            "Batch",
        ],
        "fields": [
            "name",
            "description",
            "sku",
            "quantity",
            "price",
            "cost",
            "location",
            "supplier",
            "order_date",
            "customer",
            "address",
            "status",
            "tracking_number",
            "weight",
            "dimensions",
            "reorder_level",
            "last_received",
        ],
    },
    "saas": {  # Added SaaS domain
        "nouns": [
            "Tenant",
            "Organization",
            "User",
            "Subscription",
            "Plan",
            "Feature",
            "Invoice",
            "Billing",
            "ApiKey",
            "Role",
            "Permission",
            "Workspace",
            "Project",
        ],
        "fields": [
            "name",
            "subdomain",
            "owner",
            "plan",
            "status",
            "trial_ends_at",
            "created_at",
            "updated_at",
            "is_active",
            "feature_flags",
            "billing_address",
            "invoice_number",
            "amount",
            "due_date",
            "paid_date",
            "api_key_value",
            "role_name",
            "description",
            "user_limit",
            "storage_limit",
        ],
    },
    "generic": {
        "nouns": [
            "Item",
            "Record",
            "Entry",
            "Data",
            "Object",
            "Element",
            "Unit",
            "Component",
            "Node",
            "Entity",
            "Thing",
        ],
        "fields": [
            "name",
            "value",
            "description",
            "identifier",
            "timestamp",
            "flag",
            "status",
            "notes",
            "field_a",
            "field_b",
            "related_item",
            "parent",
            "child",
            "attribute",
            "code",
            "label",
        ],
    },
}


def get_model_name(domain, existing_names):
    """
    Generates a plausible, unique model name based on domain.

    Args:
        domain (str): The selected domain.
        existing_names (set): A set of already used model names.

    Returns:
        str: A unique model name.
    """
    if domain not in DOMAIN_WORDS:
        domain = "generic"  # Fallback

    attempts = 0
    max_attempts = 20  # Prevent infinite loops for finding unique name
    while attempts < max_attempts:
        base_name = random.choice(DOMAIN_WORDS[domain]["nouns"])
        # Add a small chance of a two-word name for variety
        if random.random() < 0.2:
            adj = random.choice(DOMAIN_WORDS[domain]["nouns"])  # Reusing noun list
            if adj != base_name:
                base_name = f"{adj}{base_name}"  # Simple concatenation

        model_name = base_name
        # Ensure uniqueness (simple check, might need refinement for complex cases)
        if model_name not in existing_names:
            return model_name
        attempts += 1

    # Fallback if domain words fail to produce unique name quickly
    while True:
        model_name = f"GenericModel_{generate_random_suffix(5)}"
        if model_name not in existing_names:
            return model_name


def get_field_name(domain, existing_fields):
    """
    Generates a plausible, unique field name based on domain.

    Args:
        domain (str): The selected domain.
        existing_fields (set): A set of field names already used in the current model.

    Returns:
        str: A unique field name for the model.
    """
    if domain not in DOMAIN_WORDS:
        domain = "generic"

    attempts = 0
    max_attempts = 20  # Prevent infinite loops
    while attempts < max_attempts:
        base_name = random.choice(DOMAIN_WORDS[domain]["fields"])
        # Ensure the generated name is a valid Python identifier (simple check)
        if not base_name.isidentifier():
            base_name = base_name.replace("-", "_").replace(
                " ", "_"
            )  # Basic sanitization
            if not base_name.isidentifier() or base_name.startswith("_"):
                base_name = f"field_{base_name}"  # Prefix if needed

        # Add suffix for uniqueness if the base name is already taken
        field_name = base_name
        suffix_num = 1
        while field_name in existing_fields:
            field_name = f"{base_name}_{suffix_num}"
            suffix_num += 1

        if field_name not in existing_fields and field_name.isidentifier():
            return field_name
        attempts += 1

    # Fallback if domain words fail to produce unique name quickly
    while True:
        field_name = f"generic_field_{generate_random_suffix(5)}"
        if field_name not in existing_fields and field_name.isidentifier():
            return field_name


# --- Code Generation Functions ---


def generate_models_code(models_data):
    """
    Generates the Python code content for the models.py file.

    Args:
        models_data (dict): A dictionary where keys are model names and values are
                            dictionaries of {field_name: field_definition_string}.
                            May contain a special key '__imports__' for necessary imports.

    Returns:
        str: The complete code for models.py.
    """
    # Start with standard imports
    import_lines = ["from django.db import models"]
    # Add specific imports if needed (e.g., for UUID)
    if models_data.get("__imports__"):
        import_lines.extend(models_data["__imports__"])
    # Add other common imports
    import_lines.append("from django.utils.text import slugify")
    import_lines.append(
        "from django.conf import settings # Example if User model needed"
    )
    # Add uuid import only if UUIDField is actually used in models_data
    uuid_needed = False
    for model_name in models_data:
        if model_name == "__imports__":
            continue
        for field_def in models_data[model_name].values():
            if "UUIDField" in field_def:
                uuid_needed = True
                break
        if uuid_needed:
            break
    if uuid_needed:
        import_lines.append("import uuid")

    imports = (
        "\n".join(sorted(list(set(import_lines)))) + "\n\n"
    )  # Sort and unique imports

    code = imports
    model_definitions = []

    # Generate models in alphabetical order for consistency
    model_names = sorted([k for k in models_data if k != "__imports__"])

    for model_name in model_names:
        model_code = ""
        fields = models_data[model_name]
        model_code += f"class {model_name}(models.Model):\n"
        model_code += f'    """Represents a {model_name.lower()} in the system."""\n'

        # Add Meta class
        model_code += "    class Meta:\n"
        model_code += f"        verbose_name = '{model_name.lower()}'\n"
        # Simple pluralization (can be improved)
        plural_name = (
            f"{model_name.lower()}s"
            if not model_name.lower().endswith("s")
            else f"{model_name.lower()}es"
        )
        model_code += f"        verbose_name_plural = '{plural_name}'\n"

        # Add ordering based on a common field if possible
        order_field = next(
            (
                fn
                for fn in fields
                if "created" in fn.lower()
                or "date" in fn.lower()
                or "timestamp" in fn.lower()
            ),
            None,
        )
        if not order_field:
            order_field = next(
                (
                    fn
                    for fn in fields
                    if "name" in fn.lower()
                    or "title" in fn.lower()
                    or "order" in fn.lower()
                ),
                None,
            )
        if order_field:
            # Use '-' for descending order (newest first)
            order_prefix = (
                "-"
                if (
                    "date" in order_field.lower()
                    or "created" in order_field.lower()
                    or "timestamp" in order_field.lower()
                )
                else ""
            )
            model_code += f"        ordering = ['{order_prefix}{order_field}']\n"
        else:
            model_code += "        # ordering = ['id'] # Default ordering\n"
        model_code += "\n"

        if not fields:
            model_code += "    # No fields defined for this model yet.\n"
            model_code += "    pass\n"
        else:
            # Generate fields in alphabetical order for consistency
            for field_name in sorted(fields.keys()):
                field_def = fields[field_name]
                model_code += f"    {field_name} = {field_def}\n"
            model_code += "\n"  # Blank line after fields

        # Generate __str__ method
        model_code += "    def __str__(self):\n"
        # Try to find a suitable field for the string representation
        str_field = next(
            (
                fn
                for fn, fd in fields.items()
                if "name" in fn.lower()
                or "title" in fn.lower()
                or "email" in fn.lower()
                or "subdomain" in fn.lower()
            ),
            None,
        )
        if not str_field:
            str_field = next(
                (
                    fn
                    for fn, fd in fields.items()
                    if "CharField" in fd or "SlugField" in fd
                ),
                None,
            )

        if str_field:
            # Ensure the output is a string, especially for non-string fields
            model_code += f"        return str(self.{str_field}) if self.{str_field} else f'{{self.__class__.__name__}} (ID: {{self.pk}})'\n"
        else:  # Fallback if no suitable field found
            model_code += (
                "        return f'{self.__class__.__name__} object (ID: {self.pk})'\n"
            )
        model_code += "\n"

        # Optional: Add a simple example method (e.g., get_absolute_url stub)
        # model_code += f"    def get_absolute_url(self):\n"
        # model_code += f"        # Placeholder: Implement URL reversing if needed\n"
        # model_code += f"        # from django.urls import reverse\n"
        # model_code += f"        # return reverse('{model_name.lower()}_detail', kwargs={{'pk': self.pk}})\n"
        # model_code += f"        return f'/{model_name.lower()}/{self.pk}/'\n"
        # model_code += "\n"

        model_definitions.append(model_code)

    # Join model definitions with double newlines
    code += "\n\n".join(model_definitions)

    return code


def generate_forms_code(model_names, app_name):
    """
    Generates the Python code content for the forms.py file.

    Args:
        model_names (list): A list of strings, the names of the generated models.
        app_name (str): The name of the Django app.

    Returns:
        str: The complete code for forms.py.
    """
    if not model_names:
        return "# No models generated, so no forms created.\n"

    imports = "from django import forms\n"
    # Correct relative import for models within the same app
    # Import models alphabetically
    imports += f"from .models import {', '.join(sorted(model_names))}\n\n"
    code = imports
    form_definitions = []

    # Generate forms in alphabetical order
    for model_name in sorted(model_names):
        form_code = ""
        form_code += f"class {model_name}Form(forms.ModelForm):\n"
        form_code += f'    """Basic ModelForm for the {model_name} model."""\n'
        form_code += "    class Meta:\n"
        form_code += f"        model = {model_name}\n"
        # Using '__all__' as specified in the requirements (has_forms=True implies basic forms)
        form_code += "        fields = '__all__'\n"
        # Example of excluding fields:
        # form_code += f"        # exclude = ['created_at', 'updated_at'] # Example\n"
        # Example of specifying widgets:
        # form_code += f"        # widgets = {{\n"
        # form_code += f"        #     'description': forms.Textarea(attrs={{'rows': 3}}),\n"
        # form_code += f"        # }}\n"
        form_definitions.append(form_code)

    # Join form definitions with double newlines
    code += "\n\n".join(form_definitions)

    return code


# --- Main Generator Logic ---


def generate_django_app(
    app_name, num_models, avg_fields, relation_density, domain, target_app_path
):
    """
    Generates the synthetic Django app directory and files inside a target path.

    Args:
        app_name (str): The name for the app directory.
        num_models (int): The number of models to generate.
        avg_fields (int): The target average number of non-relation fields per model.
        relation_density (float): The approximate probability (0.0 to 1.0) that a model
                                  will have at least one outgoing ForeignKey.
        domain (str): The thematic domain ('blog', 'inventory', 'saas', 'generic') for naming.
        target_app_path (Path): The full path where the app directory should be created.
    """

    print(f"--- Generating Synthetic Django App '{app_name}' --- ")
    # Domain, model count, etc. already printed by main block
    # print(f"Domain: {domain}")
    # print(f"Number of Models: {num_models}")
    # print(f"Avg Fields per Model: {avg_fields}")
    # print(f"Relation (ForeignKey) Density: {relation_density}")
    # print("---------------------------------------")

    # --- 1. Create App Directory ---
    # Ensure the target directory exists
    try:
        os.makedirs(target_app_path, exist_ok=True)
        print(f"Ensured app directory exists: {target_app_path}")
    except OSError as e:
        print(f"Error creating directory {target_app_path}: {e}")
        raise  # Re-raise the exception to be caught by the main block

    # Create __init__.py
    init_path = target_app_path / "__init__.py"
    try:
        with open(init_path, "w") as f:
            pass  # Create empty file
    except IOError as e:
        print(f"Error creating file {init_path}: {e}")
        raise

    # --- 2. Plan Models ---
    # (Same logic as before)
    model_names_set = set()
    for _ in range(num_models):
        model_names_set.add(get_model_name(domain, model_names_set))

    effective_num_models = num_models
    if len(model_names_set) < num_models:
        print(
            f"Warning: Could only generate {len(model_names_set)} unique model names due to potential collisions."
        )
        effective_num_models = len(model_names_set)  # Adjust count

    model_names = list(model_names_set)  # Convert back to list
    models_data = {
        name: {} for name in model_names
    }  # {model_name: {field_name: field_def}}
    models_data["__imports__"] = []  # Initialize list for potential imports

    print(f"Planned models for '{app_name}': {', '.join(sorted(model_names))}")

    # --- 3. Generate Fields and Relations ---
    # (Same field generation logic as before)
    # ... [omitting the lengthy field generation code for brevity, it remains the same] ...
    basic_field_types = [
        "models.CharField(max_length=100, blank=True, db_index=True)",  # Added db_index
        "models.CharField(max_length=255, unique=True)",
        "models.TextField(blank=True, help_text='Enter description here.')",
        "models.IntegerField(default=0)",
        "models.PositiveIntegerField(default=0)",
        "models.FloatField(null=True, blank=True)",  # Allow null for floats
        "models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)",  # Increased precision
        "models.BooleanField(default=False)",
        "models.DateField(null=True, blank=True)",
        "models.DateTimeField(auto_now_add=True)",  # Created timestamp
        "models.DateTimeField(auto_now=True)",  # Updated timestamp
        "models.EmailField(max_length=254, blank=True, unique=True)",  # Often unique
        "models.URLField(blank=True, max_length=500)",  # Increased length
        "models.SlugField(max_length=100, unique=True, blank=True)",
        "models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=False)",  # Ensure not PK by default
        "models.JSONField(default=dict, blank=True)",  # Added JSONField
        # Example ForeignKey to User (requires User model import)
        # f"models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')",
    ]
    # Add uuid import if UUIDField is used
    if any("UUIDField" in f for f in basic_field_types):
        if "import uuid" not in models_data["__imports__"]:
            # Check if uuid already added by model data generation loop below
            pass  # Logic moved into generate_models_code

    for model_name in model_names:
        current_fields = set()  # Use set for faster unique checks
        generated_fields_dict = {}  # Store generated {name: def}

        # Determine number of basic fields for this model, ensuring at least 1
        # Using Poisson distribution might be slightly more realistic for counts
        num_basic_fields = (
            max(1, np.random.poisson(avg_fields))
            if avg_fields > 0
            else 1  # Use numpy.random.poisson
        )  # Requires numpy

        # Add basic fields
        for _ in range(num_basic_fields):
            field_name = get_field_name(domain, current_fields)
            field_def = random.choice(basic_field_types)

            # Special handling for SlugField - try to base it on another field
            if "SlugField" in field_def:
                potential_source = next(
                    (
                        fn
                        for fn in generated_fields_dict
                        if "name" in fn or "title" in fn
                    ),
                    None,
                )
                field_def += (
                    f" # Auto-populated from '{potential_source}' field in save()"
                    if potential_source
                    else " # Should be auto-populated in save()"
                )

            # Add field to tracking
            current_fields.add(field_name)
            generated_fields_dict[field_name] = field_def

        # Add ForeignKey relations based on density
        # Adjust effective density based on model count
        effective_relation_density = relation_density
        if effective_num_models <= 1:
            effective_relation_density = 0.0
        # Only add if there are other models to link to and density check passes
        if effective_num_models > 1 and random.random() < effective_relation_density:
            possible_targets = [m for m in model_names if m != model_name]
            if possible_targets:
                target_model = random.choice(possible_targets)
                # Generate a plausible name for the foreign key field
                fk_base_name = target_model.lower()
                fk_field_name = get_field_name(
                    domain, current_fields
                )  # Use naming function for FK too
                # Ensure FK name is reasonably related if possible, fallback otherwise
                if (
                    fk_base_name not in fk_field_name and random.random() < 0.7
                ):  # High chance to make it related
                    fk_field_name = (
                        fk_base_name
                        if fk_base_name not in current_fields
                        else f"{fk_base_name}_link"
                    )
                    # Ensure uniqueness again
                    suffix_num = 1
                    while fk_field_name in current_fields:
                        fk_field_name = f"{fk_base_name}_{suffix_num}"
                        suffix_num += 1

                # Define the ForeignKey field
                # Add related_name to prevent reverse accessor clashes
                # Make related_name more predictable if possible
                related_name = f"{model_name.lower()}_{fk_field_name}_related"  # Pattern: child_fkfield_related
                related_name = related_name.replace(
                    "__", "_"
                )  # Clean up double underscores

                fk_def = (
                    f"models.ForeignKey('{target_model}', "
                    f"on_delete=models.SET_NULL, "  # Use SET_NULL or PROTECT as safer defaults than CASCADE
                    f"null=True, blank=True, "
                    f"related_name='{related_name}', "
                    f"db_index=True)"  # Index foreign keys
                )
                # Add field to tracking
                current_fields.add(fk_field_name)
                generated_fields_dict[fk_field_name] = fk_def
                print(
                    f"  - Added relation: {model_name}.{fk_field_name} -> {target_model}"
                )

        models_data[model_name] = generated_fields_dict

    # --- 4. Write models.py ---
    models_code = generate_models_code(models_data)
    models_path = target_app_path / "models.py"
    try:
        with open(models_path, "w", encoding="utf-8") as f:
            f.write(models_code)
        print(f"Generated models file: {models_path}")
    except IOError as e:
        print(f"Error writing file {models_path}: {e}")
        raise

    # --- 5. Write forms.py ---
    forms_code = generate_forms_code(model_names, app_name)
    forms_path = target_app_path / "forms.py"
    try:
        with open(forms_path, "w", encoding="utf-8") as f:
            f.write(forms_code)
        print(f"Generated forms file: {forms_path}")
    except IOError as e:
        print(f"Error writing file {forms_path}: {e}")
        # Don't necessarily stop if forms fail, models might be useful
        print("Warning: Failed to write forms file, continuing...")

    print(f"--- App '{app_name}' generation complete --- ")


# --- Command-Line Interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a synthetic Django project using a template, including a generated app.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # --- Arguments for App Generation (passed to generate_django_app) ---
    parser.add_argument(
        "--app_name",
        default="synthetic_app",
        help="Name of the Django app directory to create within the project.",
    )
    parser.add_argument(
        "--num_models",
        type=str,
        default="small",
        choices=["small", "medium", "large"],
        help="Size category for the number of models: 'small' (<=8), 'medium' (<=13), 'large' (<=21).",
    )
    parser.add_argument(
        "--avg_fields",
        type=int,
        default=random.choice([3, 5, 8]),
        choices=[3, 5, 8],
        help="Target average number of non-relational fields per model.",
    )
    parser.add_argument(
        "--relation_density",
        type=float,
        default=random.choice([0.0, 0.3, 0.6]),
        choices=[0.0, 0.3, 0.6],
        help="Approximate probability (0.0 to 0.6) a model has >= 1 outgoing ForeignKey.",
    )
    parser.add_argument(
        "--domain",
        default=random.choice(["blog", "inventory", "saas", "generic"]),
        choices=["blog", "inventory", "saas", "generic"],
        help="Semantic domain for generating model/field names.",
    )
    # Add new argument for output directory
    parser.add_argument(
        "--output_dir",
        default="generated_projects",
        help="Directory where the generated project will be created.",
    )
    # --- Arguments for Project Scaffolding ---
    # No specific arguments for project name yet, it will be generated

    args = parser.parse_args()

    # --- Determine Actual Number of Models ---
    model_size_map = {
        "small": (1, 8),  # Range: 1 to 8
        "medium": (9, 13),  # Range: 9 to 13
        "large": (14, 21),  # Range: 14 to 21
    }
    min_models, max_models = model_size_map.get(
        args.num_models, (1, 8)
    )  # Default to small range
    actual_num_models = random.randint(
        min_models, max_models
    )  # Generate random number within the category range
    print(
        f"Selected model category: '{args.num_models}' (range {min_models}-{max_models} models)"
    )
    print(f"Generating {actual_num_models} model(s).")

    # --- Input Validation ---
    if args.avg_fields < 0:
        parser.error("Average fields per model (--avg_fields) cannot be negative.")
    if not (0.0 <= args.relation_density <= 1.0):
        parser.error(
            "Relation density (--relation_density) must be between 0.0 and 1.0."
        )

    # --- Template and Paths Setup ---
    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir / "host_template"
    if not template_dir.is_dir():
        print(f"Error: Template directory not found at {template_dir}")
        print(
            "Please ensure 'host_template' exists in the same directory as the script."
        )
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = script_dir / args.output_dir
    output_dir.mkdir(exist_ok=True)

    # --- Generate Project Name & Path ---
    try:
        project_name = generate_unique_project_name(output_dir)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    project_dir = output_dir / project_name
    print(f"Target project directory: {project_dir}")

    # --- 1. Copy Host Template ---
    try:
        shutil.copytree(
            template_dir, project_dir, dirs_exist_ok=False
        )  # Don't overwrite
        print(f"Copied template from '{template_dir.name}' to '{project_dir.name}'")
    except FileExistsError:
        print(f"Error: Target project directory '{project_dir}' already exists.")
        sys.exit(1)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        # Attempt cleanup if copy failed partway?
        if project_dir.exists():
            try:
                shutil.rmtree(project_dir)
            except Exception as cleanup_e:
                print(f"Error during cleanup: {cleanup_e}")
        sys.exit(1)

    # --- 2. Generate App Inside Project ---
    app_dir = project_dir / args.app_name  # App created inside the new project dir
    try:
        # Call the refactored app generation function
        generate_django_app(
            app_name=args.app_name,
            num_models=actual_num_models,
            avg_fields=args.avg_fields,
            relation_density=args.relation_density,  # Pass raw density, function handles adjustment
            domain=args.domain,
            target_app_path=app_dir,  # Pass the target path for the app
        )
    except Exception as e:
        print(f"Error during app generation: {e}")
        # Cleanup the created project directory
        print(f"Cleaning up partially created project '{project_dir}'...")
        shutil.rmtree(project_dir)
        sys.exit(1)

    # --- 3. Modify settings.py ---
    # Path inside the copied project directory
    settings_path = project_dir / "project_placeholder" / "settings.py"
    marker = "# SYNTHETIC_APP_INSTALL_MARKER"
    app_install_line = f"    '{args.app_name}', # Added by generator"
    try:
        content = settings_path.read_text(encoding="utf-8")
        if marker not in content:
            print(
                f"Warning: Placeholder '{marker}' not found in {settings_path}. App not added to INSTALLED_APPS."
            )
        else:
            new_content = content.replace(marker, app_install_line)
            settings_path.write_text(new_content, encoding="utf-8")
            print(f"Updated INSTALLED_APPS in {settings_path.relative_to(script_dir)}")
    except Exception as e:
        print(
            f"Error updating settings file {settings_path.relative_to(script_dir)}: {e}"
        )
        # Cleanup the created project directory
        print(f"Cleaning up partially created project '{project_dir}'...")
        shutil.rmtree(project_dir)
        sys.exit(1)

    # --- (Optional Renaming Logic - Skipped for now) ---
    # If we renamed project_placeholder, we'd need to update:
    # - ROOT_URLCONF in settings.py
    # - WSGI_APPLICATION in settings.py
    # - Possibly manage.py? (Check DJANGO_SETTINGS_MODULE)

    print("\n--- Project Generation Complete ---")
    print(
        f"Synthetic Django project created at: {project_dir.relative_to(script_dir.parent)}"
    )  # Show path relative to workspace
    print(f"App '{args.app_name}' generated inside.")
    print("\nTo test:")
    print(f'  cd "{project_dir.relative_to(script_dir)}"')  # Use relative path for cd
    print(f"  python manage.py makemigrations {args.app_name}")
    print("  python manage.py migrate")
    print("  # (Optional) Create a superuser to access admin:")
    print("  # python manage.py createsuperuser")
    print("  python manage.py runserver")
