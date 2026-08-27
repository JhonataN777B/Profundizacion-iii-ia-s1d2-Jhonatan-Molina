# Plan de migración: simulación de tenis de mesa

## Alcance

Este documento planifica la migración del script MATLAB
`legacy/TableTennisTests (2).mlx` a Python. La primera fase debe reproducir
la semántica actual del modelo, con el integrador de paso fijo, y separar el
núcleo de simulación de la visualización. No incluye una traducción de código
ni cambios al archivo legacy.

## Módulos propuestos

| Módulo | Responsabilidad |
| --- | --- |
| `models.py` | Definir estructuras de datos tipadas (por ejemplo, `dataclass`) para la pelota, mesa, red, parámetros físicos, configuración numérica, estado inicial, estado instantáneo y trayectoria. |
| `validation.py` | Validar rangos y consistencia de parámetros: valores positivos, restituciones entre 0 y 1, `dt` positivo, vectores tridimensionales y horizonte temporal válido. |
| `forces.py` | Calcular fuerza gravitacional, arrastre lineal, fuerza de Magnus, torque de arrastre rotacional y las aceleraciones lineal y angular resultantes. No debe producir gráficos ni modificar configuración. |
| `integrator.py` | Aplicar un paso de integración Euler semiimplícito: actualizar aceleración, velocidad y posición; y, de forma análoga, aceleración angular, velocidad angular y orientación. |
| `collisions.py` | Detectar y resolver colisiones con mesa y red. Inicialmente debe conservar la regla legacy; posteriormente podrá incorporar detección continua por eventos. |
| `simulation.py` | Exponer `simulate(config, initial_state) -> Trajectory`; coordinar el bucle temporal, integrador y colisiones, sin depender de interfaces gráficas. |
| `scenarios.py` | Declarar escenarios reproducibles. Debe incluir el escenario legacy, con sus parámetros y condiciones iniciales, como referencia de regresión. |
| `visualization.py` | Dibujar mesa, red, pelota, vectores y gráficas temporales con Matplotlib. Debe aceptar una `Trajectory` ya calculada y ser completamente opcional. |
| `cli.py` o notebook | Punto de entrada para ejecutar un escenario, guardar resultados y solicitar visualización. No debe contener física de simulación. |

## Parámetros de simulación

La configuración debe conservar unidades explícitas: milímetros (mm), segundos
(s), gramos (g), milinewtons (mN), radianes (rad). La implementación deberá
documentar cada unidad junto a su campo.

| Grupo | Parámetro legacy | Valor inicial de referencia | Unidad / uso |
| --- | --- | ---: | --- |
| Pelota | `ball_mass` | 2.7 | g |
| Pelota | `ball_radius` | 20.25 | mm |
| Pelota | `ball_rot_inertia` | `2/3 * mass * radius^2` | g·mm² |
| Mesa | `table_length`, `table_width`, `table_height` | 2740, 1525, 760 | mm |
| Red | `net_height`, `net_extra` | 152.5, 180 | mm |
| Colisiones | `table_restitution`, `net_restitution`, `table_friction` | 0.77, 0.5, 0.25 | coeficientes sin dimensión |
| Fuerzas | `g`, `drag`, `rot_drag`, `magnus` | 9800, 2.7, 350.0, 0.01 | según las unidades definidas por el modelo legacy |
| Tiempo | `dt`, duración | 0.005, 1.5 | s |
| Estado inicial | posición `x0` | `[0, 762.5, 1065]` | mm |
| Estado inicial | velocidad `v0` | `[7000, -3000, -3000]` | mm/s |
| Estado inicial | velocidad angular `omega0` | `[0, 0, 75] * 2π` | rad/s |
| Visualización | `animate`, `plot_period`, `yaw`, `pitch` | `true`, 5, -45, pendiente de confirmar | configuración de interfaz |

La asignación MATLAB `pitch = 23,5;` debe tratarse como una ambigüedad a
resolver antes de fijar la configuración: es probable que el valor deseado sea
`23.5`, mientras que MATLAB interpreta la coma como separador de expresiones.

## Variables de salida

`simulate` debe devolver una estructura `Trajectory`, con una muestra por
instante de tiempo y sin efectos de interfaz gráfica.

| Variable | Forma esperada | Descripción |
| --- | --- | --- |
| `time` | `(n_steps,)` | Tiempo de cada muestra, en s. |
| `position` | `(n_steps, 3)` | Posición de la pelota, en mm. |
| `velocity` | `(n_steps, 3)` | Velocidad lineal, en mm/s. |
| `acceleration` | `(n_steps, 3)` | Aceleración lineal, en mm/s². |
| `orientation` | `(n_steps, 3)` | Ángulo rotacional acumulado, en rad. |
| `angular_velocity` | `(n_steps, 3)` | Velocidad angular, en rad/s. |
| `angular_acceleration` | `(n_steps, 3)` | Aceleración angular, en rad/s². |
| `events` (recomendado) | secuencia de eventos | Colisiones detectadas, índice temporal y tipo (`table` o `net`). Puede añadirse sin alterar las series anteriores. |

Para facilitar la comparación inicial con MATLAB, el número de muestras debe
ser `len(np.arange(0, duration + tolerancia, dt))` o, preferiblemente, una
convención documentada que reproduzca exactamente los instantes inclusivos del
vector `0:dt:duration` del legado.

## Criterios mínimos de verificación

1. El escenario legacy se ejecuta sin visualización y devuelve series con las
   siete variables anteriores, dimensión temporal coherente y valores finitos.
2. La primera muestra de posición, velocidad y velocidad angular coincide
   exactamente con el estado inicial configurado.
3. Con Magnus, arrastre y gravedad desactivados, y sin colisiones durante el
   intervalo, la velocidad lineal se mantiene constante y la posición sigue la
   actualización Euler semiimplícita definida.
4. Con arrastre rotacional activado y sin otras interacciones, la magnitud de
   la velocidad angular no aumenta.
5. Una colisión válida con la mesa sitúa la pelota en
   `table_height + ball_radius` y deja la componente vertical de velocidad con
   signo ascendente tras aplicar restitución.
6. Una colisión válida con la red aplica la regla legacy de reflexión y
   amortiguación sobre el eje longitudinal y la velocidad angular.
7. La ejecución del escenario de referencia produce resultados numéricos
   comparables al legado para los primeros pasos y para una selección de
   instantes acordados, usando tolerancias explícitas. La comparación visual es
   complementaria, no el único criterio de aceptación.
8. La visualización consume una trayectoria precalculada y no cambia ninguno
   de sus datos.

## Riesgos conocidos y decisiones pendientes

- **Unidades y consistencia dimensional:** los comentarios describen algunos
  coeficientes, pero conviene revisar dimensionalmente el término de Magnus y
  los factores de fuerza/torque antes de reinterpretarlos o normalizarlos.
- **Colisión con red incompleta:** el legacy indica expresamente que requiere
  mejora. Mientras la pelota permanece en su volumen, la regla puede aplicarse
  en más de un paso y causar reflexiones repetidas.
- **Túnel por paso discreto:** con `dt = 0.005 s` y velocidades elevadas, la
  pelota puede cruzar mesa o red entre dos muestras. La primera versión debe
  conservar este comportamiento para regresión; una fase posterior puede usar
  detección continua de impactos.
- **Modelo de fricción ad hoc:** la transferencia entre velocidad lineal y
  angular en el rebote no está justificada ni calibrada dentro del archivo.
- **Cobertura física limitada:** no hay colisiones con suelo, bordes laterales
  ni una condición de fin de jugada al salir del área de interés.
- **Convención vectorial:** MATLAB utiliza vectores columna `(3, n)` y `cross`;
  Python debe fijar una convención única, recomendablemente `(n_steps, 3)`, y
  probar explícitamente los productos cruzados.
- **Inercia rotacional:** el factor `2/3` debe conservarse en la versión de
  compatibilidad, pero su interpretación física debe confirmarse antes de una
  revisión del modelo.
- **Parámetros visuales no físicos:** `pitch = 23,5` debe confirmarse y la
  animación no debe formar parte del núcleo ni de las pruebas numéricas.

## Secuencia recomendada

1. Definir datos, unidades y validaciones.
2. Implementar el núcleo puro con compatibilidad numérica frente al escenario
   legacy, sin gráficos.
3. Añadir pruebas unitarias y una prueba de regresión de trayectoria.
4. Incorporar gráficas y animación como capa independiente.
5. Evaluar mejoras físicas (eventos de colisión, modelo de red y fricción) en
   una fase separada, con nuevas referencias de aceptación.
