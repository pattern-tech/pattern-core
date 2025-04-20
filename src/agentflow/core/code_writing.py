import re
import os

from typing import List
from src.agentflow.llm.llm_wrapper import create_llm_wrapper
from src.agentflow.prompts.prompt_hub import FIX_CODE_ERROR_PROMPT
from src.agentflow.prompts.prompt_hub import CODE_WRITING_USER_PROMPT
from src.util.configuration import Config


class CodeGenerator:
    def __init__(self):
        """Initialize CodeGenerator with the configured LLM."""
        config = Config.get_config()
        self.llm = create_llm_wrapper(
            service=config["llm"]["provider"],
            model_name=config["llm"]["model"],
            api_key=config["llm"]["api_key"],
            stream=False,
            callbacks=None
        )
        self.model = config["llm"]["model"]

    def set_chat_history(self, set_chat_history):
        """Set custom user input for code generation"""
        self.set_chat_history = set_chat_history

    def set_MCR(self, MCR):
        """Set custom tools schema for code generation"""
        self.MCR = MCR

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

    def generate_code(self):
        # """Generate Python code based on user input and system prompt"""

        user_prompt = CODE_WRITING_USER_PROMPT.format(
            MCR=self.MCR,
            chat_history=self.set_chat_history[:-1],
            user_task=self.set_chat_history[-1]
        )

        messages = [
            ("developer", self.system_prompt),
            ("human", user_prompt)
        ]

        response = self.llm.invoke(messages)
        return self.extract_code(response.content)

    def execute_code(self, code, imports: str):
        """Execute the generated code and return the result"""
        if imports:
            code = f"{imports}\n\n" + code
            print(f"Executing code\n-----------\n{code}\n-----------")
        try:
            namespace = {}
            exec(code, namespace)
            return namespace.get('final_result', None), None
        except Exception as e:
            return None, str(e)

    def fix_code_with_llm(self, code, error):
        """Use LLM to fix code that caused an exception"""

        prompt = FIX_CODE_ERROR_PROMPT.format(code=code, error=error)

        messages = [
            ("developer", "You are an expert Python developer who specializes in fixing code errors. Provide only the corrected code without explanations."),
            ("human", prompt)
        ]

        response = self.llm.invoke(messages)
        return self.extract_code(response.content)

    def generate_and_execute(self, imports=None, max_attempts=3):
        """Generate and execute code in one step with automatic error correction"""
        code = self.generate_code()

        print(code)

        result, error = self.execute_code(code, imports)
        attempt = 1

        while error and attempt < max_attempts:
            print(f"Attempt {attempt} failed with error: {error}")
            print("Using LLM to fix the code...")

            # Feed the error and code to LLM for fixing
            fixed_code = self.fix_code_with_llm(code, error)
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
