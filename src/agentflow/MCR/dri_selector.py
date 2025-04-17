import json

from typing import List, Dict, Any, Optional, Callable

from src.util.configuration import Config
from src.agentflow.MCR.mcr import get_mcr_for_llm
from src.agentflow.utils.shared_tools import init_llm
from src.agentflow.prompts.prompt_hub import DRI_SELECTION_PROMPT


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
            callbacks=None
        )

    @staticmethod
    def _get_llm():
        """Get initialized LLM instance."""
        config = Config.get_config()
        return init_llm(
            service=config["llm"]["provider"],
            model_name=config["llm"]["model"],
            api_key=config["llm"]["api_key"],
            stream=False,
            callbacks=None
        )

    @staticmethod
    def select_DRI(query: List[str]) -> List[Any]:
        """
        Select appropriate DRIs for a given user query.

        Args:
            query (List[str]): List of user queries

        Returns:
            List[Any]: List of selected DRIs
        """
        # Get MCR
        MCR = get_mcr_for_llm()

        print(f"MCR: {MCR}")
        print("-----------------------------------")

        # Get LLM response
        messages = [
            ("system", DRI_SELECTION_PROMPT.format(MCR=MCR)),
            ("human", "selected DIRs: ")
        ]

        # Use the static method to get the LLM
        llm = DRISelector._get_llm()
        response = llm.invoke(messages)

        print(f"LLM response: {response.content}")

        # Parse the response to get selected tool names
        try:
            DIR_IDs = DRISelector._parse_DIR_selection_response(
                response.content)

            print(DIR_IDs)

            return DIR_IDs

        except Exception as e:
            print(f"Error parsing DIR from LLM response: {e}")
            # Return MCR as fallback if parsing fails
            return MCR

    @staticmethod
    def _parse_DIR_selection_response(response: str) -> List[str]:
        """
        Parse the LLM response to extract selected DIR IDs.

        Args:
            response (str): The LLM's response

        Returns:
            List[str]: List of selected DIR IDs
        """
        # Clean up the response to extract just the JSON part
        response = response.strip()

        # Handle potential formatting issues
        if not response.startswith('['):
            # Try to find the JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']')

            if start_idx != -1 and end_idx != -1:
                response = response[start_idx:end_idx+1]
            else:
                # If no JSON array is found, return an empty list
                return []

        try:
            # Parse the JSON array
            DIR_IDs = json.loads(response)

            # Ensure it's a list of strings
            if isinstance(DIR_IDs, list) and all(isinstance(item, str) for item in DIR_IDs):
                return DIR_IDs
            else:
                return []
        except json.JSONDecodeError:
            # If parsing fails, return an empty list
            return []
