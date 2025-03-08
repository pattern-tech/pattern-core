import re
from pydantic import BaseModel, Field

WALLET_REGEX = re.compile(r'^0x[a-fA-F0-9]{40}$')


class WalletAddress(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):  # Accept the extra parameter
        if not isinstance(v, str):
            raise TypeError("String required")
        if not WALLET_REGEX.fullmatch(v):
            raise ValueError("Invalid wallet address format")
        return cls(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {
            "type": "string",
            "pattern": r'^0x[a-fA-F0-9]{40}$',
            "examples": ["0x0123456789abcdef0123456789abcdef01234567"],
        }
