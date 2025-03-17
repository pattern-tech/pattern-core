import re
import os

from typing import List
from openai import OpenAI
from src.agentflow.prompts.prompt_hub import CODE_EXECUTION_PROMPT, FIX_CODE_ERROR_PROMPT


class CodeGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        self.system_prompt = CODE_EXECUTION_PROMPT

    def set_user_input(self, user_input):
        """Set custom user input for code generation"""
        self.user_input = user_input

    def set_tools_schema(self, tools_schema):
        """Set custom tools schema for code generation"""
        self.tools_schema = tools_schema

    def set_system_prompt(self, system_prompt):
        """Set custom system prompt for code generation"""
        self.system_prompt = system_prompt

    def extract_code(self, markdown_text):
        """Extract Python code from markdown text"""
        # Pattern to match a Python code block in markdown
        pattern = r"```python\s*([\s\S]*?)```"
        match = re.search(pattern, markdown_text)
        if match:
            return match.group(1).strip()
        return ""

    def generate_code(self, model="gpt-4o-mini"):
        """Generate Python code based on user input and system prompt"""
        body = f"functions schema:\n-----------\n{self.tools_schema}\n-----------\nuser_task: {self.user_input}"
        messages = [
            {"role": "developer", "content": self.system_prompt},
            {"role": "user", "content": body}
        ]

        completion = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        return self.extract_code(completion.choices[0].message.content)

    def execute_code(self, code, imports: List):
        """Execute the generated code and return the result"""
        if imports:
            code = f"{imports}\n" + code
            print(f"Executing code\n-----------\n{code}\n-----------")
        try:
            namespace = {}
            exec(code, namespace)
            return namespace.get('final_result', None), None
        except Exception as e:
            return None, str(e)

    def fix_code_with_llm(self, code, error, model="gpt-4o-mini"):
        """Use LLM to fix code that caused an exception"""
        prompt = FIX_CODE_ERROR_PROMPT.format(code=code, error=error)

        messages = [
            {"role": "developer", "content": "You are an expert Python developer who specializes in fixing code errors. Provide only the corrected code without explanations."},
            {"role": "user", "content": prompt}
        ]

        completion = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        return self.extract_code(completion.choices[0].message.content)

    def generate_and_execute(self, imports=None, model="gpt-4o-mini", max_attempts=3):
        """Generate and execute code in one step with automatic error correction"""
        code = self.generate_code(model)
        result, error = self.execute_code(code, imports)
        attempt = 1

        while error and attempt < max_attempts:
            print(f"Attempt {attempt} failed with error: {error}")
            print("Using LLM to fix the code...")

            # Feed the error and code to LLM for fixing
            fixed_code = self.fix_code_with_llm(code, error, model)
            code = fixed_code  # Update the code with the fixed version

            # Try executing the fixed code
            result, error = self.execute_code(code, imports)
            attempt += 1

        if error:
            print(
                f"Failed after {max_attempts} attempts. Final error: {error}")
        else:
            print("The result is:", result)

        return result, error, code  # Return the final code as well
