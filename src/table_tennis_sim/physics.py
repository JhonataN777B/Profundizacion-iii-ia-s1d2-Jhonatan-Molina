"""Cálculos físicos aislados para la simulación de la pelota."""

import numpy as np
from numpy.typing import NDArray

from .parameters import SimulationParameters


Vector = NDArray[np.float64]


def calculate_linear_acceleration(
    velocity: Vector,
    angular_velocity: Vector,
    parameters: SimulationParameters,
) -> Vector:
    """Calcula la aceleración lineal de la pelota.

    Args:
        velocity: Velocidad lineal actual, en mm/s.
        angular_velocity: Velocidad angular actual, en rad/s.
        parameters: Parámetros físicos de la simulación.

    Returns:
        Aceleración lineal de la pelota, en mm/s².
    """

    gravity_force = parameters.gravity * parameters.ball_mass * np.array(
        [0.0, 0.0, -1.0]
    )
    drag_force = -parameters.drag * velocity
    magnus_force = parameters.magnus * np.cross(angular_velocity, velocity)
    return (gravity_force + drag_force + magnus_force) / parameters.ball_mass


def calculate_angular_acceleration(
    angular_velocity: Vector,
    parameters: SimulationParameters,
) -> Vector:
    """Calcula la aceleración angular causada por arrastre rotacional."""

    torque = -parameters.rotational_drag * angular_velocity
    return torque / parameters.rotational_inertia
