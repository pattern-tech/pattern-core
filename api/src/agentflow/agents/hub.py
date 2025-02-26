from src.agentflow.agents import ether_scan_agent, goldrush_agent


class _Agent():
    def __init__(self, name, reference):
        self.name = name
        self.reference = reference


class AgentHub():
    """
    A hub for managing different agents.

    Attributes:
        ETHER_SCAN_AGENT: An instance of the etherscan agent.
        GOLDRUSH_AGENT: An instance of the goldrush agent.
    """
    ETHER_SCAN = _Agent(name="ETHER_SCAN",
                        reference=goldrush_agent.goldrush_agent)
    GOLDRUSH = _Agent(name="GOLDRUSH",
                      reference=goldrush_agent.goldrush_agent)
