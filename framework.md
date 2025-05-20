# LLM Code Generation Evaluation Framework

## Overview

This framework evaluates LLM performance in implementing a unified client-document creation form for a law firm document management system. It focuses on practical implementation, measurable metrics, and real-world interaction patterns.

## Influences

This framework is influenced by two key perspectives:

1. **The Second Half of AI** (Shunyu Yao, 2025)
   - Moving beyond benchmark-focused evaluation to real-world utility
   - Questioning traditional i.i.d. (independent and identically distributed) evaluation assumptions
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

### 1. Python Code Quality Delta (30%)

- Measured by `step_01_run_tests.py` and `step_02_check_python_code_quality.py`
- Components:
  - Test coverage delta (after - before)
  - Number of new failed tests (after - before)
  - Pylint score delta (after - before)
- Scoring:
  - If any old tests fail: 0 points
  - If no new failures: (coverage_delta + pylint_delta) / 2
  - Example:
    - Before: 80% coverage, 8.0 pylint
    - After: 85% coverage, 8.5 pylint
    - Delta: +5% coverage, +0.5 pylint = 2.75 points

### 2. Template Code Quality Delta (20%)

- Measured by `step_03_check_template_quality.py`
- Components:
  - Total issues delta (after - before)
  - Categories: accessibility, inline styles, template tags, JavaScript, structure
- Scoring:
  - Formula: max(0, 10 - (issues_delta / 5))
  - Example:
    - Before: 30 issues
    - After: 40 issues
    - Delta: +10 issues = 8 points (10 - (10/5))

### 3. Number of Prompts (15%)

- Manual count of prompts needed to complete the task
- Lower is better
- Scoring:
  - Formula: max(0, 10 - (prompt_count / 2))
  - Example:
    - 4 prompts = 8 points
    - 10 prompts = 5 points
    - 20+ prompts = 0 points

### 4. LLM-as-Judge Explanation Clarity (15%)

- Automated evaluation of code explanation quality
- Scale: 1-5
- Scoring:
  - Formula: (score / 5) * 10
  - Example: 4/5 = 8 points

### 5. Task Completion Efficiency (20%)

- Measured by:
  - Field efficiency ratio (actual_fields / minimum_required_fields)
    - Closer to 1.0 is better
    - Example: 8 fields when only 6 are needed = 0.75
  - Number of form submissions needed
    - Lower is better
    - Example: 2 submissions = 8 points
- Scoring:
  - Field efficiency: min(10, field_ratio * 10)
    - Example: 0.75 ratio = 7.5 points
  - Form submissions: max(0, 10 - (submission_count * 2))
    - Example: 2 submissions = 6 points
  - Final score: average of the two
  - Example:
    - Field efficiency: 7.5 points
    - Form submissions: 6 points
    - Final: 6.75 points

## Final Score Calculation

```
Final Score =
  (Python Quality Delta * 0.30) +
  (Template Quality Delta * 0.20) +
  (Prompt Efficiency * 0.15) +
  (Explanation Clarity * 0.15) +
  (Task Efficiency * 0.20)
```

Example:

- Python Quality Delta: 2.75/10 * 0.30 = 0.83
- Template Quality Delta: 8/10 * 0.20 = 1.60
- Prompt Efficiency: 8/10 * 0.15 = 1.20
- Explanation Clarity: 8/10 * 0.15 = 1.20
- Task Efficiency: 6.75/10 * 0.20 = 1.35
- Total Score: 6.18/10

## Results Template

```
Project: Law Firm Document Management
LLM: [Claude 3.7/Gemini Pro 2.5]
Date: [Date]

Python Code Quality Delta: ___/10 (30%)
- Coverage Delta: ___%
- Pylint Score Delta: ___/10
- New Failed Tests: ___

Template Quality Delta: ___/10 (20%)
- Issues Delta: ___

Prompt Efficiency: ___/10 (15%)
- Number of Prompts: ___ (lower is better)

Explanation Clarity: ___/10 (15%)
- LLM-as-Judge Score: ___/5

Task Efficiency: ___/10 (20%)
- Field Efficiency Ratio: ___ (closer to 1.0 is better)
- Number of Form Submissions: ___ (lower is better)

Final Score: ___/10
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

## Results

### Claude 3.7 Sonnet
- Python Code Quality Delta: 0/10 (30%)
  - Coverage Delta: -12%
  - Pylint Score Delta: -0.25
  - New Failed Tests: 1
- Template Quality Delta: 8.4/10 (20%)
  - Issues Delta: +8
- Prompt Efficiency: 9.5/10 (15%)
  - Number of Prompts: 1
- Explanation Clarity: 8/10 (15%)
  - LLM-as-Judge Score: 4/5
- Task Efficiency: 8/10 (20%)
  - All tests passing: 4/5
  - End-to-end working: Yes
- Final Score: 6.53/10

### Gemini 2.5 Pro
- Python Code Quality Delta: -2.54/10 (30%)
  - Coverage Delta: -5%
  - Pylint Score Delta: -0.08
  - New Failed Tests: 0
- Template Quality Delta: 8.8/10 (20%)
  - Issues Delta: +6
- Prompt Efficiency: 9.5/10 (15%)
  - Number of Prompts: 1
- Explanation Clarity: 8/10 (15%)
  - LLM-as-Judge Score: 4/5
- Task Efficiency: 9/10 (20%)
  - All tests passing: 5/5
  - End-to-end working: Yes
- Final Score: 6.12/10
