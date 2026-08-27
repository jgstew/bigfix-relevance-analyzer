"""bigfix-relevance-analyzer: work with BigFix Relevance generically (extract, analyze, etc.)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bigfix-relevance-analyzer")
except PackageNotFoundError:  # pragma: no cover - only hit for an uninstalled checkout
    __version__ = "0.0.0"

__all__ = ["__version__"]
