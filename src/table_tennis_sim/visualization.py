"""Gráficas estáticas para resultados de simulación.

Este módulo no anima ni modifica los resultados: solamente los representa con
Matplotlib después de que la simulación termina.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from numpy.typing import NDArray

from .simulation import SimulationResult


COMPONENT_LABELS = ("x", "y", "z")
COMPONENT_COLORS = ("tab:red", "tab:green", "tab:blue")
FloatArray = NDArray[float]


def plot_trajectory_3d(result: SimulationResult) -> Figure:
    """Crea una gráfica 3D de la trayectoria de la pelota.

    Args:
        result: Series temporales devueltas por ``simulate``.

    Returns:
        La figura de Matplotlib creada. El llamador puede mostrarla con
        ``plt.show()`` o guardarla con ``figure.savefig(...)``.
    """

    figure = plt.figure(figsize=(8, 6))
    axes = figure.add_subplot(projection="3d")
    position = result.position

    axes.plot(
        position[:, 0],
        position[:, 1],
        position[:, 2],
        color="tab:blue",
        label="Trayectoria",
    )
    axes.scatter(*position[0], color="tab:green", label="Inicio", zorder=3)
    axes.scatter(*position[-1], color="tab:red", label="Fin", zorder=3)
    axes.set_title("Trayectoria 3D de la pelota")
    axes.set_xlabel("x (mm)")
    axes.set_ylabel("y (mm)")
    axes.set_zlabel("z (mm)")
    axes.legend()
    figure.tight_layout()
    return figure


def _plot_components(
    time: FloatArray,
    values: FloatArray,
    title: str,
    y_label: str,
) -> Figure:
    """Crea una gráfica temporal de las tres componentes de un vector."""

    figure, axes = plt.subplots(figsize=(8, 4.5))
    for index, (label, color) in enumerate(zip(COMPONENT_LABELS, COMPONENT_COLORS)):
        axes.plot(time, values[:, index], label=label, color=color)

    axes.set_title(title)
    axes.set_xlabel("Tiempo (s)")
    axes.set_ylabel(y_label)
    axes.grid(visible=True, alpha=0.3)
    axes.legend(title="Componente")
    figure.tight_layout()
    return figure


def plot_position(result: SimulationResult) -> Figure:
    """Crea una gráfica de posición por componente en función del tiempo."""

    return _plot_components(
        result.time,
        result.position,
        title="Posición de la pelota",
        y_label="Posición (mm)",
    )


def plot_velocity(result: SimulationResult) -> Figure:
    """Crea una gráfica de velocidad lineal por componente."""

    return _plot_components(
        result.time,
        result.velocity,
        title="Velocidad lineal de la pelota",
        y_label="Velocidad (mm/s)",
    )


def plot_angular_velocity(result: SimulationResult) -> Figure:
    """Crea una gráfica de velocidad angular por componente."""

    return _plot_components(
        result.time,
        result.angular_velocity,
        title="Velocidad angular de la pelota",
        y_label="Velocidad angular (rad/s)",
    )


def plot_all(result: SimulationResult) -> tuple[Figure, Figure, Figure, Figure]:
    """Crea las cuatro visualizaciones estáticas del resultado.

    Las gráficas temporales se devuelven como figuras separadas para evitar una
    cuadrícula de subplots demasiado densa.
    """

    return (
        plot_trajectory_3d(result),
        plot_position(result),
        plot_velocity(result),
        plot_angular_velocity(result),
    )
