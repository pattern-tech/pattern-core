from enum import Enum
from langchain import hub


class AgentType(Enum):
    """
    Enum for agent types.

    ROUTER_AGENT: Router agent.
    SUB_AGENT: Sub agent.
    """
    ROUTER_AGENT = "router_agent"
    BLOCKCHAIN_AGENT = "blockchain_agent"
    REACT_AGENT = "react_agent"
    PATTERN_CORE_AGENT = "pattern_core_agent"


class Prompt():
    """
    Registry for prompts.

    BLOCKCHAIN_AGENT: Prompt for the blockchain agent.
    ROUTER_AGENT: Prompt for the router agent.
    REACT_AGENT: Prompt for the react agent.
    PATTERN_CORE_AGENT: Prompt for the pattern core agent.
    """
    BLOCKCHAIN_AGENT = hub.pull("pattern-agent/eth-agent")
    ROUTER_AGENT = hub.pull("pattern-agent/pattern-agent")
    REACT_AGENT = hub.pull("hwchase17/react")
    PATTERN_CORE_AGENT = hub.pull("pattern-agent/pattern-core-agent")
