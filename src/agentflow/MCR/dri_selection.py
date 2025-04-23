import json

from typing import List, Dict, Any, Optional, Callable, Tuple

from src.util.configuration import Config
from src.agentflow.MCR.mcr import get_mcr_for_llm
from src.agentflow.utils.shared_tools import init_llm
from src.agentflow.prompts.prompt_hub import DRI_SELECTION_SYSTEM_PROMPT, DRI_SELECTION_USER_PROMPT
from src.share.logging import Logging


class DRISelector:
    """
    A module that uses an LLM to select appropriate DRI based on a user query.
    It analyzes the query and MCR to determine which DRIs are most relevant.
    """

    def __init__(self):
        """Initialize the ToolSelector with an LLM."""
        self._logger = Logging().get_logger()
        self._logger.info("Initializing DRISelector")

        config = Config.get_config()
        self._logger.debug(
            f"Using LLM provider: {config['llm']['provider']}, model: {config['llm']['model']}")

        self.llm = init_llm(
            service=config["llm"]["provider"],
            model_name=config["llm"]["model"],
            api_key=config["llm"]["api_key"],
            stream=False,
            callbacks=None,
        )

    def select_DRI(self, query: List[str]) -> Tuple[str, Any]:
        """
        Select appropriate DRIs for a given user query.

        Args:
            query (List[str]): List of user queries

        Returns:
            Tuple[str, Any]: A tuple containing:
                - status type ("selected_DRI", "missing_input", etc.)
                - result data (list of DIRs or message string)
        """
        # Get MCR
        MCR = get_mcr_for_llm()

        self._logger.debug(
            f"Retrieved {len(MCR)} MCR entries for DRI selection")

        for DRI in MCR:
            self._logger.debug(
                f"Available DRI: {DRI['ID']} - {DRI['DESCRIPTION'][:50]}...")

        # Get LLM response
        messages = [
            ("system", DRI_SELECTION_SYSTEM_PROMPT),
            ("human", DRI_SELECTION_USER_PROMPT.format(
                previous_user_queries=query[:-1],
                user_task=query[-1],
                MCR=MCR
            ))
        ]

        self._logger.info(
            f"Sending DRI selection request to LLM for user query: {query[-1][:50]}...")

        # Use the LLM to get a response
        try:
            response = self.llm.invoke(messages)
            self._logger.debug("Received response from LLM")

            # Parse the response to get selected tool names
            message, result = self._parse_DIR_selection_response(
                response.content)

            if message == "selected_DRI":
                self._logger.info(f"Selected {len(result)} DRIs: {result}")
            else:
                self._logger.info(
                    f"DRI selection result: {message} - {result}")

            return (message, result)

        except Exception as e:
            self._logger.error(
                f"Error in LLM DRI selection: {e}", exc_info=True)
            return "not_supported_task", f"Error in DRI selection: {str(e)}"

    def _parse_DIR_selection_response(self, response: str) -> Tuple[str, Any]:
        """
        Parse the LLM response to extract selected DIR IDs or identify missing inputs or unsupported tasks.

        Args:
            response (str): The LLM's response

        Returns:
            Tuple[str, Any]: A tuple containing:
                - status type ("selected_DRI", "missing_input", or "not_supported_task")
                - message (list of DIRs or message string)
        """
        self._logger.debug("Parsing DRI selection response")
        response = response.strip()
        self._logger.debug(f"Raw LLM response: {response[:100]}...")

        # Check for tool selection format
        tool_start = response.find("<tool>")
        tool_end = response.find("</tool>")
        if tool_start != -1 and tool_end != -1:
            tool_content = response[tool_start + 6:tool_end].strip()
            try:
                selected_DIRs = json.loads(tool_content)
                if isinstance(selected_DIRs, list):
                    self._logger.info(
                        f"Successfully parsed {len(selected_DIRs)} DRIs from response")
                    return "selected_DRI", selected_DIRs
            except json.JSONDecodeError as e:
                self._logger.error(f"Error parsing DIR IDs from response: {e}")
                return "not_supported_task", []

        # If none of the expected formats are found, try to handle legacy format or return error
        self._logger.warning(
            "Response didn't match expected format. Attempting legacy parsing.")
        try:
            if response.startswith('[') and response.endswith(']'):
                selected_DIRs = json.loads(response)
                if isinstance(selected_DIRs, list):
                    self._logger.info(
                        f"Successfully parsed {len(selected_DIRs)} DRIs using legacy format")
                    return "selected_DRI", selected_DIRs
        except json.JSONDecodeError:
            self._logger.error(
                "Failed to parse response as JSON array in legacy format")
            pass

        # Default fallback for unrecognized formats
        self._logger.error(
            f"Could not parse response format: {response[:50]}...")
        return "not_supported_task", "Could not parse response format"
