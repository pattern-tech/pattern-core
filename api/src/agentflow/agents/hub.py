from src.agentflow.agents import ether_scan_agent, goldrush_agent
from typing import Any, List


class AgentHub:
    """
    A hub for managing and retrieving different agents.

    Attributes:
        agents (dict): A dictionary mapping agent names to their respective agent instances.

    Methods:
        get_agents(agent_names: list[str]) -> list:
            Static method to retrieve a list of agents based on the provided agent names.
    """

    def __init__(self):
        self.agents = {
            "etherscan": ether_scan_agent.etherscan_agent,
            "goldrush": goldrush_agent.goldrush_agent
        }

    def get_agents(self, agent_names: List[str]) -> List[Any]:
        """
        Retrieve a list of agent instances based on the provided agent names.

        Args:
            agent_names (list[str]): A list of agent names to retrieve.

        Returns:
            list: A list of agent instances corresponding to the provided agent names.
                  If an agent name is not found, it is ignored.
        """
        return [self.agents[agent_name] for agent_name in agent_names if agent_name in self.agents.keys()]
