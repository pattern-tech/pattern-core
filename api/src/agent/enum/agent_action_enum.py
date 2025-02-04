from enum import Enum


class AgentActionEnum(str, Enum):
    NO_ACTION = "no_action"
    INPUT_TEXT = "input_text"
    INPUT_MEDIA = "input_media"
