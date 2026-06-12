"""Harite package init."""
__version__ = "2.0.0"

from .cli import run as run  # expose run for console_scripts
from . import plugins as plugins  # expose plugins for discovery (explicit re-export for linters)
from . import workspace as workspace  # expose workspace helpers
