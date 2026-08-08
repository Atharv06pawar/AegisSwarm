import sys

# Retrieves standard library logging module objects bootstrapped into sys.modules
std_logging = sys.modules.get("logging")
std_handlers = sys.modules.get("logging.handlers")
