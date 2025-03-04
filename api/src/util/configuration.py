import os
import json

from src.util.singleton import Singleton
from src.util.execptions import *

class Config(metaclass=Singleton):
    def __init__(self) -> None:
        self._config = self._parse_config("config.json")
        self._check_config(self._config)

    @classmethod
    def get_config(cls) -> dict:
        # internally retrieve the singleton instance, then return its config
        instance = cls()  # calls the Singleton metaclass, so it's still a singleton
        return instance._config

    def _parse_config(self, file_path: str) -> dict:
        """
        Parse a JSON configuration file and returns its contents as a dictionary.

        Args:
            file_path (str): The path to the JSON configuration file.

        Returns:
            dict: The contents of the JSON configuration file.
        """
        if not os.path.exists(file_path):
            raise ConfigNotFoundError()
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

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
            # check if ollama is seted the host and models in extra_params should be seted
            if "host" not in config["llm"]["extra_params"]:
                raise ConfigKeyError("extra_params | host")
            if "models" not in config["llm"]["extra_params"]:
                raise ConfigKeyError("extra_params | models")

        for service in config["services"]:
            if "name" not in service:
                raise ConfigKeyError("services | name")
            if "url" not in service:
                raise ConfigKeyError("services | url")
            if "api_key" not in service:
                raise ConfigKeyError("services | api_key")

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
