_Trabajo de Fin de Grado realizado por Lucía García Bobillo._

# ChromaVision

ChromaVision es una herramienta modular basada en visión artificial, que permite detectar piezas físicas por color y posición, y visualizarlas en un motor de videojuegos
de forma sincronizada. El color de cada pieza actúa como un identificador que permite sustituirla por el tipo de objeto que el usuario desee en el motor.

## Estructura del repositorio

- `detection_module/` – Código fuente del módulo de detección.
- `visualization_module/` – Código fuente de módulo de visualización de Unreal Engine (5.7).
- `ChromaVisionUE/` – Proyecto de Unreal Engine (C++ / Blueprints) de la aplicación de demostración (con el módulo de visualización incluido).
- `tools/` – Cuentagotas que indica el color BGR y HSV del píxel seleccionado con el ratón sobre la imagen de la webcam.
- `debug/` – Versiones de desarrollo y pruebas conservadas como registro.
- `executables/` – Ejecutable del módulo de detección.
