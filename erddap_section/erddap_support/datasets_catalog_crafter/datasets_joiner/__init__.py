"""
This Python module reads individual XML datasets from a specified folder and combines them into a single concatenated string. During the merging process,
the module performs filtering to exclude invalid or unnecessary data and applies validation to ensure the integrity of the XML format.
"""

from .join_datasets import DatasetCatalogJoiner
