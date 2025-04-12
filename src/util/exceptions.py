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
        super().__init__(f"{self.message}")


class NotFoundError(Exception):
    """Exception raised when something"""

    def __init__(self, message="not found"):
        self.message = message
        super().__init__(f"{self.message}")


class InvalidMessageError(Exception):
    """Exception raised when an item not found."""

    def __init__(self, message="invalid message"):
        self.message = message
        super().__init__(f"{self.message}")


class InvalidSignatureError(Exception):
    """Exception raised when the signature in invalid"""

    def __init__(self, message="invalid signature"):
        self.message = message
        super().__init__(f"{self.message}")


class InvalidPasswordError(Exception):
    """Exception raised when the password in invalid"""

    def __init__(self, message="invalid password"):
        self.message = message
        super().__init__(f"{self.message}")


class AlreadyExistsError(Exception):
    """Exception raised when something is already exists"""

    def __init__(self, message="duplicate"):
        self.message = message
        super().__init__(f"{self.message}")


class JWTDecodeError(Exception):
    """Exception raised when the JWT is invalid"""

    def __init__(self, message="invalid JWT"):
        self.message = message
        super().__init__(f"{self.message}")


class InvalidTokenError(Exception):
    """Exception raised when the token is invalid"""

    def __init__(self, message="invalid token"):
        self.message = message
        super().__init__(f"{self.message}")


class RateLimitError(Exception):
    """Exception raised when the rate limit is exceeded"""

    def __init__(self, message="rate limit exceeded"):
        self.message = message
        super().__init__(self.message)


class NotSupportedError(Exception):
    """Exception raised when something is not supported yet"""

    def __init__(self, message="is not supported yet"):
        self.message = message
        super().__init__(self.message)
