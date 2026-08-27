"""Simulación numérica de una pelota de tenis de mesa.

La implementación conserva el esquema Euler semiimplícito y las reglas de
colisión del script MATLAB legacy. No incluye animación ni gráficos.
"""

from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

from .parameters import InitialState, SimulationParameters
from .physics import calculate_angular_acceleration, calculate_linear_acceleration


FloatArray = NDArray[np.float64]


class SimulationResult(NamedTuple):
    """Trayectoria numérica de una simulación.

    Las matrices de estado tienen forma ``(n_steps, 3)`` y emplean la
    convención de componentes ``(x, y, z)``. Al ser una ``NamedTuple``, el
    resultado puede consultarse por nombre o desempaquetarse directamente.
    """

    time: FloatArray
    position: FloatArray
    velocity: FloatArray
    orientation: FloatArray
    angular_velocity: FloatArray


def _as_vector(values: tuple[float, float, float], name: str) -> FloatArray:
    """Convierte una tupla de entrada en un vector NumPy de tres componentes."""

    vector = np.asarray(values, dtype=float)
    if vector.shape != (3,):
        raise ValueError(f"{name} debe tener exactamente tres componentes.")
    return vector


def _collide_with_table(
    position: FloatArray,
    velocity: FloatArray,
    angular_velocity: FloatArray,
    parameters: SimulationParameters,
) -> None:
    """Aplica la respuesta de rebote de mesa usada en el modelo MATLAB."""

    is_over_table = (
        0.0 < position[0] < parameters.table_length
        and 0.0 < position[1] < parameters.table_width
    )
    hits_table = position[2] < parameters.table_height + parameters.ball_radius
    if not (is_over_table and hits_table):
        return

    position[2] = parameters.table_height + parameters.ball_radius
    contact_radius = np.array([0.0, 0.0, parameters.ball_radius])
    linear_velocity_xy = np.array([velocity[0], velocity[1], 0.0])
    linear_rotation_difference = (
        np.cross(angular_velocity, contact_radius) - linear_velocity_xy
    )
    velocity += parameters.table_friction * linear_rotation_difference
    angular_velocity += (
        parameters.table_friction
        * np.cross(linear_rotation_difference, np.array([0.0, 0.0, 1.0]))
        / parameters.ball_radius
    )
    velocity[2] = -parameters.table_restitution * velocity[2]


def _collide_with_net(
    position: FloatArray,
    velocity: FloatArray,
    angular_velocity: FloatArray,
    parameters: SimulationParameters,
) -> None:
    """Aplica la respuesta simplificada de red usada en el modelo MATLAB."""

    touches_net_x = (
        parameters.table_length / 2.0 - parameters.ball_radius
        <= position[0]
        <= parameters.table_length / 2.0 + parameters.ball_radius
    )
    touches_net_y = -parameters.net_extra < position[1] < (
        parameters.table_width + parameters.net_extra
    )
    touches_net_z = (
        parameters.table_height + parameters.ball_radius
        < position[2]
        < parameters.table_height + parameters.net_height + parameters.ball_radius
    )
    if touches_net_x and touches_net_y and touches_net_z:
        angular_velocity *= parameters.net_restitution
        velocity[0] = -parameters.net_restitution * velocity[0]


def simulate(
    parameters: SimulationParameters,
    initial_state: InitialState,
) -> SimulationResult:
    """Calcula una trayectoria, sin crear figuras ni animaciones.

    Args:
        parameters: Parámetros físicos, geométricos y de integración.
        initial_state: Posición, velocidad lineal y velocidad angular iniciales.

    Returns:
        Una ``SimulationResult`` desempaquetable como ``time, position,
        velocity, orientation, angular_velocity``.
    """

    parameters.validate()
    initial_position = _as_vector(initial_state.position, "position")
    initial_velocity = _as_vector(initial_state.velocity, "velocity")
    initial_angular_velocity = _as_vector(
        initial_state.angular_velocity, "angular_velocity"
    )

    step_count = int(np.floor(parameters.duration / parameters.time_step)) + 1
    time = np.arange(step_count, dtype=float) * parameters.time_step
    position = np.zeros((step_count, 3), dtype=float)
    velocity = np.zeros((step_count, 3), dtype=float)
    orientation = np.zeros((step_count, 3), dtype=float)
    angular_velocity = np.zeros((step_count, 3), dtype=float)

    position[0] = initial_position
    velocity[0] = initial_velocity
    angular_velocity[0] = initial_angular_velocity

    for step in range(1, step_count):
        linear_acceleration = calculate_linear_acceleration(
            velocity[step - 1], angular_velocity[step - 1], parameters
        )
        velocity[step] = velocity[step - 1] + linear_acceleration * parameters.time_step
        position[step] = position[step - 1] + velocity[step] * parameters.time_step

        angular_acceleration = calculate_angular_acceleration(
            angular_velocity[step - 1], parameters
        )
        angular_velocity[step] = (
            angular_velocity[step - 1]
            + angular_acceleration * parameters.time_step
        )
        orientation[step] = (
            orientation[step - 1] + angular_velocity[step] * parameters.time_step
        )

        _collide_with_table(
            position[step], velocity[step], angular_velocity[step], parameters
        )
        _collide_with_net(
            position[step], velocity[step], angular_velocity[step], parameters
        )

    return SimulationResult(time, position, velocity, orientation, angular_velocity)
