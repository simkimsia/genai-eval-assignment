# LLM Code Generation Evaluation Framework

## Overview

This framework evaluates LLM performance in implementing a unified client-document creation form for a law firm document management system. It focuses on practical implementation, measurable metrics, and real-world interaction patterns.

## Influences

This framework is influenced by two key perspectives:

1. **The Second Half of AI** (Shunyu Yao, 2025)
   - Moving beyond benchmark-focused evaluation to real-world utility
   - Questioning traditional i.i.d. evaluation assumptions
   - Emphasizing interactive, human-in-the-loop evaluation
   - Focusing on practical implementation over theoretical performance

2. **Real-world Developer Experience**
   - Practical experience using AI-assisted IDEs like Cursor since Dec 2024
   - Understanding that contextual awareness is crucial for effective code generation
   - Recognition that real development tasks are sequential and contextual
   - Experience with the importance of human-AI interaction in development workflow

These influences shape our approach to evaluation, moving away from isolated task completion towards measuring real-world utility and developer experience.

## Core Principles

1. **Real-world Utility Focus**
   - Evaluate based on practical developer experience
   - Focus on end-user value and usability
   - Prioritize maintainable, scalable solutions

2. **Interactive Development**
   - Simulate real developer workflow
   - Track context understanding across attempts
   - Measure improvement over time
   - Include human-in-the-loop evaluation

3. **Measurable Outcomes**
   - Use quantifiable metrics where possible
   - Combine automated and manual evaluation
   - Clear success criteria for each metric

## Core Metrics

### 1. Automated Metrics (60%)

#### Code Quality (30%)

- Unit test / integration test coverage (check for any regression bugs)
  - handled by: `python evaluation/step_01_run_tests.py`
  - Calculates coverage percentage across all Python files
  - Provides per-file coverage details
  - Weight: 10% of total score
  - Scoring:
    - If any tests fail: 0 points (automatic failure)
    - If all tests pass: Coverage percentage directly contributes to score (e.g., 85% coverage = 8.5 points)
  - Note: Test failures are considered critical and override coverage scoring

- Code complexity (pylint score for Python, and coverage)
  - handled by: `python evaluation/step_02_check_python_code_quality.py`
  - Pylint score (0-10) for code quality
  - Coverage percentage calculated as: (total_statements - missing_statements) / total_statements * 100
  - Includes detailed coverage breakdown per file
  - Weight: 10% of total score
  - Scoring:
    - If any tests failed in step_01: 0 points (automatic failure)
    - If all tests passed: Average of pylint score and coverage percentage (e.g., pylint 8.5 + coverage 85% = 8.5 points)

- Template complexity (custom metric for HTML templates)
  - handled by: `python evaluation/step_03_check_template_quality.py`
  - Total issues calculated as sum of:
    - Accessibility issues (missing alt text, ARIA labels, color contrast, form labels)
    - Inline styles count
    - Template tag issues (extends, blocks, includes, URLs, static files, CSRF, form errors, XSS)
    - JavaScript issues (inline scripts, event handlers, jQuery usage, fetch usage, error handling)
    - Structural issues (blocks, extends, includes, forms, scripts, nested forms, validation)
  - Lower total_issues indicates better template quality
  - Weight: 10% of total score
  - Scoring:
    - If any tests failed in step_01: 0 points (automatic failure)
    - If all tests passed: Convert issues to score using formula: max(0, 10 - (total_issues / 10))
      - Example: 50 issues = 5 points, 20 issues = 8 points, 0 issues = 10 points

#### Functionality (30%)

- Integration test pass rate for:
  - Client lookup functionality
  - Form submission
  - Document upload
  - Edge case handling

### 2. Manual Metrics (40%)

#### Developer Experience (20%)

- Number of prompts needed to complete task
- LLM-as-judge evaluation of:
  - Code explanation clarity
  - Implementation approach
  - Error handling quality

#### UI/UX Implementation (20%)

- Task completion efficiency
  - Number of clicks to complete main task
  - Number of form fields to fill
  - Number of page loads required
- Edge case handling (human evaluated)
  - Form validation errors
  - Client lookup failures
  - Document upload issues
  - Error message clarity

## Implementation Guide

### 1. Automated Testing Setup

```python
# test_client_lookup.py
def test_client_lookup():
    # Test existing client lookup
    # Test new client creation
    # Test validation errors
    pass

# test_form_submission.py
def test_form_submission():
    # Test successful submission
    # Test validation errors
    # Test file upload
    pass

# test_edge_cases.py
def test_edge_cases():
    # Test duplicate client references
    # Test invalid file types
    # Test large file uploads
    pass
```

### 2. Manual Evaluation Checklist

#### Developer Experience

- [ ] Number of prompts needed: ___
- [ ] Code explanation clarity (1-5): ___
- [ ] Implementation approach (1-5): ___
- [ ] Error handling quality (1-5): ___

#### UI/UX Implementation

- [ ] Clicks to complete task: ___
- [ ] Form fields to fill: ___
- [ ] Page loads required: ___
- [ ] Edge case handling (1-5): ___

### 3. LLM-as-Judge Prompt Template

```
Please evaluate the following code implementation:

Code:
{code_snippet}

Criteria:
1. Code explanation clarity (1-5)
2. Implementation approach (1-5)
3. Error handling quality (1-5)

Provide scores and brief justification for each criterion.
```

## Evaluation Process

1. **Initial Setup**
   - Clone base project
   - Set up test environment
   - Prepare evaluation checklist

2. **Task Implementation**
   - Record number of prompts
   - Track code changes
   - Document UI/UX decisions

3. **Testing**
   - Run automated tests
   - Document test results
   - Record edge case handling

4. **Evaluation**
   - Calculate automated metrics
   - Complete manual checklist
   - Get LLM-as-judge evaluation

## Scoring System

### Automated Score (60%)

- Code Quality (30%)
  - Unit tests (15%)
  - Integration tests (15%)
- Functionality (30%)
  - Core features (15%)
  - Edge cases (15%)

### Manual Score (40%)

- Developer Experience (20%)
  - Number of prompts (10%)
  - LLM-as-judge evaluation (10%)
- UI/UX Implementation (20%)
  - Task completion efficiency (10%)
  - Edge case handling (10%)

## Results Template

```
Project: Law Firm Document Management
LLM: [Claude 3.7/Gemini Pro 2.5]
Date: [Date]

Automated Metrics:
- Unit Test Coverage: ___%
- Integration Test Coverage: ___%
- Code Complexity Score: ___
- Template Complexity Score: ___
- Integration Test Pass Rate: ___%

Manual Metrics:
- Number of Prompts: ___
- Code Explanation Clarity: ___/5
- Implementation Approach: ___/5
- Error Handling Quality: ___/5
- Clicks to Complete: ___
- Edge Case Handling: ___/5

Final Score: ___/100
```

## Time Allocation (6 hours)

1. Setup (1 hour)
   - Environment setup
   - Test framework implementation
   - Evaluation tools preparation

2. Implementation (3 hours)
   - Task implementation
   - Testing
   - Documentation

3. Evaluation (2 hours)
   - Automated testing
   - Manual evaluation
   - LLM-as-judge evaluation
   - Score calculation
