"""Parámetros y datos de entrada de la simulación.

El modelo usa milímetros (mm), segundos (s), gramos (g), milinewtons (mN) y
radianes (rad), igual que el archivo MATLAB de referencia.
"""

from dataclasses import dataclass


Vector3 = tuple[float, float, float]
"""Vector tridimensional representado como ``(x, y, z)``."""


@dataclass(frozen=True)
class SimulationParameters:
    """Parámetros físicos, geométricos y numéricos de una simulación.

    Los valores por defecto reproducen el escenario configurado en el código
    MATLAB legacy. ``rotational_inertia`` conserva el factor ``2/3`` usado
    allí para que la primera versión Python sea comparable.
    """

    ball_mass: float = 2.7
    ball_radius: float = 20.25
    table_restitution: float = 0.77
    net_restitution: float = 0.5
    drag: float = 2.7
    rotational_drag: float = 350.0
    magnus: float = 0.01
    table_friction: float = 0.25
    table_length: float = 2740.0
    table_width: float = 1525.0
    table_height: float = 760.0
    net_height: float = 152.5
    net_extra: float = 180.0
    gravity: float = 9800.0
    time_step: float = 0.005
    duration: float = 1.5

    @property
    def rotational_inertia(self) -> float:
        """Devuelve la inercia rotacional de la pelota en g·mm²."""

        return (2.0 / 3.0) * self.ball_mass * self.ball_radius**2

    def validate(self) -> None:
        """Comprueba los valores básicos antes de iniciar una simulación.

        Raises:
            ValueError: Si algún parámetro físico o numérico no es válido.
        """

        positive_values = {
            "ball_mass": self.ball_mass,
            "ball_radius": self.ball_radius,
            "table_length": self.table_length,
            "table_width": self.table_width,
            "table_height": self.table_height,
            "net_height": self.net_height,
            "time_step": self.time_step,
            "duration": self.duration,
        }
        for name, value in positive_values.items():
            if value <= 0:
                raise ValueError(f"{name} debe ser mayor que cero.")

        for name, value in {
            "table_restitution": self.table_restitution,
            "net_restitution": self.net_restitution,
            "table_friction": self.table_friction,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} debe estar entre 0 y 1.")


@dataclass(frozen=True)
class InitialState:
    """Estado de la pelota en el instante inicial.

    Attributes:
        position: Posición inicial en mm.
        velocity: Velocidad lineal inicial en mm/s.
        angular_velocity: Velocidad angular inicial en rad/s.
    """

    position: Vector3
    velocity: Vector3
    angular_velocity: Vector3 = (0.0, 0.0, 0.0)
