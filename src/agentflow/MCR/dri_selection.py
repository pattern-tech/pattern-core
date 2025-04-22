import json

from typing import List, Dict, Any, Optional, Callable

from src.util.configuration import Config
from src.agentflow.MCR.mcr import get_mcr_for_llm
from src.agentflow.utils.shared_tools import init_llm
from src.agentflow.prompts.prompt_hub import DRI_SELECTION_SYSTEM_PROMPT, DRI_SELECTION_USER_PROMPT


class DRISelector:
    """
    A module that uses an LLM to select appropriate DRI based on a user query.
    It analyzes the query and MCR to determine which DRIs are most relevant.
    """

    def __init__(self):
        """Initialize the ToolSelector with an LLM."""
        config = Config.get_config()
        self.llm = init_llm(
            service=config["llm"]["provider"],
            model_name=config["llm"]["model"],
            api_key=config["llm"]["api_key"],
            stream=False,
            callbacks=None,
        )

    def select_DRI(self, query: List[str]) -> List[Any]:
        """
        Select appropriate DRIs for a given user query.

        Args:
            query (List[str]): List of user queries

        Returns:
            List[Any]: List of selected DRIs
        """
        # Get MCR
        MCR = get_mcr_for_llm()

        for DRI in MCR:
            print(json.dumps(
                {"ID": DRI["ID"], "DESCRIPTION": DRI["DESCRIPTION"]}, indent=1))
        print("-----------------------------------")

        # Get LLM response
        messages = [
            ("system", DRI_SELECTION_SYSTEM_PROMPT),
            ("human", DRI_SELECTION_USER_PROMPT.format(
                previous_user_queries=query[:-1],
                user_task=query[-1],
                MCR=MCR
            ))
        ]

        # Use the static method to get the LLM
        response = self.llm.invoke(messages)

        # Parse the response to get selected tool names
        try:
            message, result = self._parse_DIR_selection_response(
                response.content)

            return (message, result)

        except Exception as e:
            print(f"Error parsing DIR from LLM response: {e}")
            # Return MCR as fallback if parsing fails
            return MCR

    def _parse_DIR_selection_response(self, response: str):
        """
        Parse the LLM response to extract selected DIR IDs or identify missing inputs or unsupported tasks.

        Args:
            response (str): The LLM's response

        Returns:
            Tuple[str, Any]: A tuple containing:
                - status type ("selected_DRI", "missing_input", or "not_supported_task")
                - message (list of DIRs or message string)
        """
        response = response.strip()

        # Check for tool selection format
        tool_start = response.find("<tool>")
        tool_end = response.find("</tool>")
        if tool_start != -1 and tool_end != -1:
            tool_content = response[tool_start + 6:tool_end].strip()
            try:
                selected_DIRs = json.loads(tool_content)
                if isinstance(selected_DIRs, list):
                    return "selected_DRI", selected_DIRs
            except json.JSONDecodeError as e:
                print(f"Error parsing DIR IDs: {e}")
                return "not_supported_task", []

        # Check for missing input format
        missing_start = response.find("<missing>")
        missing_end = response.find("</missing>")
        if missing_start != -1 and missing_end != -1:
            missing_message = response[missing_start + 9:missing_end].strip()
            return "missing_input", missing_message

        # Check for not supported format
        not_supported_start = response.find("<not_supported>")
        not_supported_end = response.find("</not_supported>")
        if not_supported_start != -1 and not_supported_end != -1:
            not_supported_message = response[not_supported_start +
                                             15: not_supported_end].strip()
            return "not_supported_task", not_supported_message

        general_start = response.find("<general>")
        general_end = response.find("</general>")
        if general_start != -1 and general_end != -1:
            general_message = response[general_start + 9:general_end].strip()
            return "general", general_message

        # If none of the expected formats are found, try to handle legacy format or return error
        print("Warning: Response didn't match expected format. Attempting legacy parsing.")
        try:
            if response.startswith('[') and response.endswith(']'):
                selected_DIRs = json.loads(response)
                if isinstance(selected_DIRs, list):
                    return "selected_DRI", selected_DIRs
        except json.JSONDecodeError:
            pass

        # Default fallback for unrecognized formats
        return "not_supported_task", "Could not parse response format"
