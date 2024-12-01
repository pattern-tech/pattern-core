from abc import ABCMeta
from threading import Lock


class SingletonABCMeta(ABCMeta):
    """
    Metaclass for creating singleton classes.

    This metaclass ensures that only one instance of a class is created and
    provides thread-safety using a double-checked locking mechanism.

    Usage:
    class MySingletonClass(metaclass=SingletonABCMeta):
        # class definition

    """

    _instances = {}
    _lock = Lock()  # Lock object to ensure thread-safety

    def __call__(cls, *args, **kwargs):
        # Double-checked locking mechanism
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(type):
    """
    Metaclass for creating singleton classes.

    This metaclass ensures that only one instance of a class is created and
    provides thread-safety using a double-checked locking mechanism.

    Usage:
    class MyClass(metaclass=Singleton):
        # class definition

    """

    _instances = {}
    _lock = Lock()  # Lock object to ensure thread-safety

    def __call__(cls, *args, **kwargs):
        # Double-checked locking mechanism
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
