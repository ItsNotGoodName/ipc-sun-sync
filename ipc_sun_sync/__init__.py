from importlib import metadata

__version__ = metadata.version(__package__)
del metadata

__description__ = "Sync sunrise and sunset on Dahua IP cameras."
