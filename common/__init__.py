"""
Any function or definition shared across modules.
"""

import logging
from .utils import clean_folder
from .config import *

log_format_str = '%(asctime)s - %(process)d - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_str)
