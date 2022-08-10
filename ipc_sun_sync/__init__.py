import pkg_resources

__version__ = pkg_resources.get_distribution("ipc-sun-sync").version
del pkg_resources

__description__ = "Sync sunrise and sunset on Dahua IP cameras."
