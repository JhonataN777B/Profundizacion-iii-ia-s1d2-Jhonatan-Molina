# Simulación de tenis de mesa

## Propósito

Este proyecto implementa en Python una simulación numérica de la trayectoria de una pelota de tenis de mesa. Conserva como referencia el comportamiento del modelo MATLAB histórico `legacy/TableTennisTests (2).mlx`: gravedad, arrastre lineal y rotacional, efecto Magnus y rebotes simplificados contra la mesa y la red.

El notebook interactivo permite variar condiciones iniciales y coeficientes del modelo, recalcular la trayectoria y visualizar sus variables de estado. Las magnitudes se expresan en milímetros (mm), segundos (s), gramos (g), milinewtons (mN) y radianes (rad).

## Estructura

```text
.
├── notebooks/
│   └── 01_simulacion_interactiva.ipynb  # controles y gráficas interactivas
├── src/table_tennis_sim/
│   ├── parameters.py                    # parámetros y estado inicial
│   ├── physics.py                       # fuerzas y aceleraciones
│   ├── simulation.py                    # integración y colisiones
│   └── visualization.py                 # gráficas con Matplotlib
├── legacy/                              # referencia MATLAB original
├── docs/plan_migracion.md               # alcance y decisiones de migración
├── README.md                            # documentación de uso
└── bitacora_ia.md                       # registro de asistencia de IA
```

## Instalación

Se requiere Python 3.10 o superior. Desde la raíz del repositorio, cree un entorno virtual e instale las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy matplotlib jupyterlab ipywidgets
```

Si PowerShell impide activar el entorno, ajuste la política de ejecución para el usuario o actívelo desde otra terminal.

## Ejecución del notebook

Con el entorno activado, inicie Jupyter desde la raíz del proyecto:

```powershell
jupyter lab
```

Abra `notebooks/01_simulacion_interactiva.ipynb` y ejecute sus celdas en orden. La primera celda incorpora automáticamente `src/` a la ruta de módulos, de modo que no es necesario instalar el paquete local. Al modificar un control, el notebook recalcula la simulación y muestra cuatro figuras: trayectoria 3D, posición, velocidad lineal y velocidad angular.

## Parámetros ajustables

El notebook expone los siguientes controles:

| Grupo | Parámetro | Rango | Unidad |
| --- | --- | ---: | --- |
| Estado inicial | Velocidad `x`, `y`, `z` | `x`: -5000 a 5000; `y`: -3000 a 3000; `z`: -4000 a 4000 | mm/s |
| Estado inicial | Velocidad angular `x`, `y`, `z` | -500 a 500 | rad/s |
| Física | Arrastre lineal | 0 a 10 | coeficiente del modelo |
| Física | Efecto Magnus | 0 a 0.1 | coeficiente del modelo |
| Colisión | Restitución de mesa | 0 a 1 | adimensional |
| Colisión | Restitución de red | 0 a 1 | adimensional |
| Colisión | Fricción de mesa | 0 a 1 | adimensional |

Para modificar otros valores, cree una instancia de `SimulationParameters`. Entre ellos están masa y radio de la pelota, gravedad, dimensiones de la mesa y red, arrastre rotacional, duración y paso de tiempo. Los valores predeterminados usan `time_step=0.005` s y `duration=1.5` s. Las dimensiones, masa, radio, duración y paso deben ser positivos; las restituciones y la fricción deben estar entre 0 y 1.

## Ejemplo de uso

También es posible usar el núcleo sin abrir el notebook. En PowerShell, con el entorno activado:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -c "from table_tennis_sim import InitialState, SimulationParameters, simulate; p = SimulationParameters(duration=1.0); s = InitialState(position=(600.0, 762.0, 1100.0), velocity=(2500.0, 0.0, 1500.0), angular_velocity=(0.0, 0.0, 100.0)); r = simulate(p, s); print(f'Muestras: {len(r.time)}'); print(f'Posición final (mm): {r.position[-1]}')"
```

Para generar las cuatro gráficas en un script o en una celda:

```python
from table_tennis_sim import plot_all

figures = plot_all(r)
```

## Limitaciones conocidas

- La integración usa Euler semiimplícito con paso fijo. A velocidades altas, la pelota puede atravesar la mesa o la red entre muestras (túnel numérico).
- La colisión con la red es una regla simplificada; mientras la pelota permanezca dentro de su volumen, puede aplicarse en varios pasos y causar reflexiones repetidas.
- La fricción de mesa y la inercia rotacional (`2/3 · masa · radio²`) se conservan por compatibilidad con el modelo legado y todavía requieren validación física y calibración experimental.
- No se modelan colisiones con el suelo ni con los bordes laterales, ni hay una condición de término al salir del área de juego.
- Las unidades y la consistencia dimensional de algunos coeficientes —en especial Magnus— proceden del modelo MATLAB y no se han normalizado.
- El repositorio aún no incluye un archivo de dependencias ni pruebas automatizadas de regresión frente a MATLAB.

Consulte [docs/plan_migracion.md](docs/plan_migracion.md) para las decisiones de migración y los riesgos técnicos detallados.
