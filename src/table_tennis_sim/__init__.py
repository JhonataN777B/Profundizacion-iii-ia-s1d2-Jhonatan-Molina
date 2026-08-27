"""Simulación numérica de una pelota de tenis de mesa."""

from .parameters import InitialState, SimulationParameters, Vector3
from .simulation import SimulationResult, simulate
from .visualization import (
    plot_all,
    plot_angular_velocity,
    plot_position,
    plot_trajectory_3d,
    plot_velocity,
)

__all__ = [
    "InitialState",
    "SimulationParameters",
    "SimulationResult",
    "Vector3",
    "plot_all",
    "plot_angular_velocity",
    "plot_position",
    "plot_trajectory_3d",
    "plot_velocity",
    "simulate",
]
