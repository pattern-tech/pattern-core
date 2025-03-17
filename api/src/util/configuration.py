import os
import json

from src.util.singleton import Singleton
from src.util.execptions import *


class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self._config = self._parse_config()
        self._check_config(self._config)

    @classmethod
    def get_config(cls) -> dict:
        # internally retrieve the singleton instance, then return its config
        instance = cls()  # calls the Singleton metaclass, so it's still a singleton
        return instance._config

    def _parse_config(self) -> dict:
        """
        Parse a JSON configuration file and returns its contents as a dictionary.

        Returns:
            dict: The contents of the JSON configuration file.
        """
        config = {}

        # load agents
        if os.environ["AGENTS"]:
            agents = os.environ["AGENTS"].split(",")
            config["agents"] = agents

        for agent in agents:
            if not os.environ[f"{agent}_API_KEY"]:
                raise Exception(f"{agent}_API_KEY not found")

        # load llm
        if os.environ["LLM_PROVIDER"] and os.environ["LLM_MODEL"]:

            config["llm"] = {
                "provider": os.environ["LLM_PROVIDER"],
                "model": os.environ["LLM_MODEL"],
                "api_key": os.environ["LLM_API_KEY"]
            }

            if os.environ["LLM_PROVIDER"] == "ollama":
                config['llm']["extra_params"] = {
                    "host": os.environ["LLM_HOST"],
                    "models_path": os.environ["LLM_MODELS_PATH"]
                }
        else:
            raise Exception(
                "LLM_PROVIDER and LLM_MODEL not set in .env")

        # load services
        config["services"] = []
        if os.environ["ETHER_SCAN_API_KEY"]:
            config["services"].append(
                {
                    "name": "ETHER_SCAN",
                    "api_key": os.environ["ETHER_SCAN_API_KEY"]
                })

        if os.environ["GOLDRUSH_API_KEY"]:
            config["services"].append(
                {
                    "name": "GOLDRUSH",
                    "api_key": os.environ["GOLDRUSH_API_KEY"]
                })

        if os.environ["MORALIS_API_KEY"]:
            config["services"].append(
                {
                    "name": "MORALIS",
                    "api_key": os.environ["MORALIS_API_KEY"]
                })

        return config

    def _check_config(self, config: dict):
        """
        Validates the given configuration dictionary to ensure it contains the required keys and values.

        Args:
            config (dict): The configuration dictionary to validate.
        """
        required_keys = ['services', 'llm', 'agents']
        for key in config.keys():
            if key not in required_keys:
                raise ConfigKeyError(key)
        if config["llm"]["provider"] == "ollama":
            # check if ollama is seted the host and models in extra_params should be set
            if "host" not in config["llm"]["extra_params"]:
                raise ConfigKeyError("extra_params | host")
            if "models" not in config["llm"]["extra_params"]:
                raise ConfigKeyError("extra_params | models")

        if not config["agents"]:
            raise ItemNotFoundError("agents should not be empty")

        service_names = [service["name"] for service in config['services']]
        for agent in config['agents']:
            if agent not in [service for service in service_names]:
                raise ItemNotFoundError(f"agent {agent} not found in services")

    @classmethod
    def get_service_config(self, config: dict, service_name: str) -> dict:
        """
        Get the configuration for a specific service from the configuration file.

        Args:
            config (dict): The configuration dictionary to validate.
            service_name (str): The name of the service to get the configuration for.

        Returns:
            dict: The configuration for the specified service.
        """
        for service in config["services"]:
            if service["name"] == service_name:
                return service
        raise ItemNotFoundError(
            f"Service {service_name} not found in configuration file.")
