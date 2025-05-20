import json
import os
import re
from typing import Dict

import anthropic
from dotenv import load_dotenv


class LLMJudge:
    def __init__(self, model_name: str):
        self.model_name = model_name
        # Load environment variables
        load_dotenv()

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        self.evaluation_prompt = """
Please evaluate the following code implementation and explanation:

Implementation:
{implementation}

Explanation:
{explanation}

Criteria:
1. Code explanation clarity (1-5)
   - How well does the code explain its functionality?
   - Are comments and documentation clear and helpful?
   - Is the code self-documenting?

2. Implementation approach (1-5)
   - How well does the implementation solve the problem?
   - Is the solution elegant and maintainable?
   - Are best practices followed?

3. Error handling quality (1-5)
   - How well are edge cases handled?
   - Are error messages clear and helpful?
   - Is the error handling comprehensive?

Please provide your evaluation in the following JSON format:
{{
    "code_explanation_clarity": {{
        "score": <1-5>,
        "justification": "<brief explanation>"
    }},
    "implementation_approach": {{
        "score": <1-5>,
        "justification": "<brief explanation>"
    }},
    "error_handling_quality": {{
        "score": <1-5>,
        "justification": "<brief explanation>"
    }}
}}

Only respond with the JSON object, no additional text.
"""

    def extract_code_and_explanation(self, markdown_content: str) -> Dict[str, str]:
        """Extract code and explanation from markdown content."""
        try:
            # Extract code blocks
            code_blocks = re.findall(
                r"```(?:diff)?\n(.*?)```", markdown_content, re.DOTALL
            )
            code = "\n".join(code_blocks)

            # Extract explanation (text between code blocks)
            explanation = re.sub(r"```.*?```", "", markdown_content, flags=re.DOTALL)
            explanation = re.sub(
                r"_{3,}.*?_{3,}", "", explanation, flags=re.DOTALL
            )  # Remove markdown headers
            explanation = re.sub(
                r"^\s*$", "", explanation, flags=re.MULTILINE
            )  # Remove empty lines
            explanation = explanation.strip()

            return {"implementation": code, "explanation": explanation}
        except Exception as e:
            print(f"Error extracting code and explanation: {str(e)}")
            return {"implementation": "", "explanation": ""}

    def evaluate_code(self, markdown_content: str) -> Dict:
        """
        Evaluate code and explanation using LLM-as-judge approach.
        Returns a dictionary with scores and justifications.
        """
        try:
            # Extract code and explanation
            content = self.extract_code_and_explanation(markdown_content)

            if not content["implementation"] and not content["explanation"]:
                raise ValueError(
                    "No implementation or explanation found in the content"
                )

            # Prepare the prompt
            prompt = self.evaluation_prompt.format(
                implementation=content["implementation"],
                explanation=content["explanation"],
            )

            # Make the API call
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                temperature=0,
                system="You are an expert code reviewer evaluating code implementations. Provide clear, objective evaluations based on the given criteria.",
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse the response
            try:
                evaluation = json.loads(response.content[0].text)
                return evaluation
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response as JSON: {str(e)}")
                print(f"Raw response: {response.content[0].text}")
                raise

        except Exception as e:
            print(f"Error during LLM evaluation: {str(e)}")
            # Fallback to basic evaluation if LLM call fails
            return {
                "code_explanation_clarity": {
                    "score": min(
                        5, max(1, len(content.get("explanation", "").split()) // 100)
                    ),
                    "justification": "Fallback evaluation due to LLM error",
                },
                "implementation_approach": {
                    "score": min(
                        5, max(1, len(content.get("implementation", "").split()) // 200)
                    ),
                    "justification": "Fallback evaluation due to LLM error",
                },
                "error_handling_quality": {
                    "score": min(
                        5, max(1, content.get("implementation", "").count("error") // 2)
                    ),
                    "justification": "Fallback evaluation due to LLM error",
                },
            }

    def evaluate_implementation(self, markdown_file: str) -> Dict:
        """
        Evaluate a markdown file containing implementation and explanation.
        """
        try:
            with open(markdown_file, "r") as f:
                content = f.read()
                return self.evaluate_code(content)
        except FileNotFoundError:
            print(f"Error: File {markdown_file} not found")
            raise
        except Exception as e:
            print(f"Error reading file {markdown_file}: {str(e)}")
            raise

    def save_evaluation(self, evaluation: Dict, output_file: str):
        """
        Save evaluation results to a JSON file.
        """
        try:
            with open(output_file, "w") as f:
                json.dump(evaluation, f, indent=2)
        except Exception as e:
            print(f"Error saving evaluation to {output_file}: {str(e)}")
            raise


def main():
    try:
        # Example usage
        judge = LLMJudge("claude-3-5-haiku-latest")

        # Evaluate implementations
        claude_file = "evaluation/results/claude37-2025-05-20_09-20-enhancing-client-creation-ui-ux.md"
        gemini_file = "evaluation/results/geminipro25-2025-05-20_09-33-enhancing-client-creation-ui-ux.md"

        # Evaluate Claude's implementation
        print("Evaluating Claude's implementation...")
        claude_evaluation = judge.evaluate_implementation(claude_file)
        judge.save_evaluation(claude_evaluation, "evaluation_results_claude.json")
        print("Claude evaluation saved to evaluation_results_claude.json")

        # Evaluate Gemini's implementation
        print("Evaluating Gemini's implementation...")
        gemini_evaluation = judge.evaluate_implementation(gemini_file)
        judge.save_evaluation(gemini_evaluation, "evaluation_results_gemini.json")
        print("Gemini evaluation saved to evaluation_results_gemini.json")

    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
