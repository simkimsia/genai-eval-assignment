# How to Run Tests

This document explains different ways to run the test suite with various debugging options.

## Basic Test Commands

### 1. Show Print Statements and Verbose Output

```bash
# First select the project when prompted
python evaluation/run_tests.py -- -s -v
```

This will:

- Show all print statements (`-s`)
- Show verbose test output (`-v`)
- Run all tests

### 2. Drop into Debugger on Failure

```bash
# First select the project when prompted
python evaluation/run_tests.py -- --pdb
```

This will:

- Drop into the Python debugger when a test fails
- Allow you to inspect variables and step through code
- Run all tests

### 3. Run Specific Test with Debug Output

```bash
# First select the project when prompted
python evaluation/run_tests.py -- -s -v law_firm_docs/tests/test_client_lookup.py::test_existing_client_lookup
```

This will:

- Show print statements
- Show verbose output
- Run only the specified test

### 4. Run Specific Test with Debugger

```bash
# First select the project when prompted
python evaluation/run_tests.py -- -s -v --pdb law_firm_docs/tests/test_client_lookup.py::test_existing_client_lookup
```

This will:

- Show print statements
- Show verbose output
- Drop into debugger on failure
- Run only the specified test

### 5. Running Specific Test Groups

There are two ways to run specific groups of tests:

#### Using Test Subfolders (Recommended)

If your tests are organized in subfolders (e.g., `tests/beforetask/`), you can run all tests in that folder:

```bash
# First select the project when prompted
python evaluation/run_tests.py -- law_firm_docs/tests/beforetask/
```

This will:

- Run all tests in the specified subfolder
- Maintain test organization
- Make it easy to run related tests together

#### Using Test Name Pattern

You can also run tests matching a specific name pattern using the `-k` flag:

```bash
# First select the project when prompted
python evaluation/run_tests.py -- -k "test_beforetask"
```

This will:

- Run all tests with "test_beforetask" in their name
- Work regardless of file location
- Be useful for running tests with similar naming patterns

## Notes

- The `--` after `run_tests.py` is important as it tells the script to pass the remaining arguments to pytest
- You can combine these options in different ways
- Use `-k "test_name"` to run tests matching a specific name pattern
- Use `-x` to stop on first failure
- Use `--maxfail=n` to stop after n failures
- Always run the commands from the project root directory
- The script will prompt you to select a project first, then run the specified test

## Example Debug Output

When using `-s`, you'll see output like:

```
Response status code: 200
Response content: b'{"name": "Test Client", "email": "test@example.com"}'
Parsed data: {'name': 'Test Client', 'email': 'test@example.com'}
```

## Common Issues

1. "Project path does not exist" error:
   - Make sure you're running the command from the project root directory
   - Don't include the full path to the test file
   - Let the script handle project selection first
   - Make sure to use `--` before any pytest arguments

## Step by Step Example

1. From project root, run:

   ```bash
   python evaluation/run_tests.py -- -s -v law_firm_docs/tests/test_client_lookup.py::test_existing_client_lookup
   ```

2. When prompted, select your project number (e.g., 1 for law_firm_docs_10lzj5)
3. The test will run with the specified options
