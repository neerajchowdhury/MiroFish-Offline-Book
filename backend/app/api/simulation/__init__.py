"""Simulation API Blueprint - organized submodules."""

from flask import Blueprint

simulation_bp = Blueprint('simulation', __name__)

from . import entities
from . import preparation
from . import execution
from . import monitoring
from . import interview
from . import profiles
