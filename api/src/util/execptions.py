class ConfigNotFoundError(Exception):
    """Exception raised when the configuration file is not found."""

    def __init__(self, message="Configuration file not found"):
        self.message = message
        super().__init__(self.message)


class ConfigKeyError(Exception):
    """Exception raised when a required key is missing in the configuration file."""

    def __init__(self, key, message="not found in configuration file"):
        self.key = key
        self.message = message
        super().__init__(f"{self.key} - {self.message}")


class ItemNotFoundError(Exception):
    """Exception raised when an item not found."""

    def __init__(self, message="not found"):
        self.message = message
        super().__init__(f"{self.item} - {self.message}")
