from src.agentflow.agents import ether_scan_agent, goldrush_agent


class AgentHub():
    """
    A hub for managing different agents.

    Attributes:
        ETHER_SCAN_AGENT: An instance of the etherscan agent.
        GOLDRUSH_AGENT: An instance of the goldrush agent.
    """
    ETHER_SCAN_AGENT = ether_scan_agent.etherscan_agent
    GOLDRUSH_AGENT = goldrush_agent.goldrush_agent
