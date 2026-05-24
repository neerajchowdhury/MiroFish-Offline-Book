"""Backward-compatible re-export for the refactored simulation blueprint.

The simulation API has been split into organized submodules under the
simulation/ package. This file preserves the original import path so
that existing code (e.g., app/__init__.py) continues to work.
"""

from .simulation import simulation_bp

__all__ = ['simulation_bp']
