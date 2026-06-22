_Trabajo de Fin de Grado realizado por Lucía García Bobillo._

# ChromaVision

[![Release](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/ESPITY/TFG-ChromaVision/releases/tag/v1.0.0)

ChromaVision es una herramienta modular basada en visión artificial, que permite detectar piezas físicas por color y posición,
y visualizarlas en un motor de videojuegos de forma sincronizada. El color de cada pieza actúa como un identificador que permite
sustituirla por el tipo de objeto que el usuario desee en el motor.

Esta herramienta sirve para desarrollar aplicaciones y videojuegos colaborativos con interfaz de usuario tangible (TUI), ofreciendo
la capacidad de modificar los colores de piezas detectadas y los objetos 3D asignados.


## Arquitectura general del sistema

Se compone de dos módulos independientes:

1. **Módulo de detección de piezas**: implementado en Python con OpenCV. Detecta el color y la posición de las piezas sobre la base y
   envía esta información al módulo de visualización en el motor de videojuegos mediante sockets UDP.
2. **Módulo de visualización**: script integrado en el proyecto del motor de videojuegos. Recibe e interpreta la lista con las piezas detectadas.
   Instancia los objetos que el usuario ha asignado a cada color, en la posición correspondiente a la pieza física.

Este módulo de visualización se ha desarrollado para Unreal Engine y se puede reutilizar en otros proyectos. Sin embargo, gracias a la conexión
estándar por UDP y al envío de mensajes en formato JSON, es posible emplear cualquier motor capaz de manejar este tipo de sockets e interpretar el formato.

Además, se ha creado una aplicación de prototipado de niveles para demostrar su funcionamiento.


## Estructura del repositorio

- `detection_module/` – Código fuente del módulo de detección (Python/OpenCV).
- `visualization_module/` – Código fuente del módulo de visualización (Unreal Engine 5.7, C++).
- `ChromaVisionUE/` – Proyecto de Unreal Engine (C++ y Blueprints) con la aplicación de demostración (prototipado de niveles). Tiene el módulo de visualización integrado.
- `tools/` – Cuentagotas que indica el color BGR y HSV del píxel seleccionado con el ratón sobre la imagen de la webcam.
- `debug/` – Scripts de depuración.
  - `base_detection_debug.py` – Algoritmo de detección de base mediante HoughLines, ejecutable de forma independiente y con visualización de depuración. Versión previa a la optimización de reducción de resolución.

Los ejecutables listos para usar (módulo de detección y aplicación de demostración) se encuentran en la sección [Releases](https://github.com/ESPITY/TFG-ChromaVision/releases).


## Requisitos

- Webcam
- Base y piezas de colores (recomendable LEGO)
- Ordenador

**En caso de querer integrar la herramienta en un nuevo proyecto de Unreal Engine:**
- ChromaVision.exe (ejecutable del módulo de detección)
- Unreal Engine 5.7
- Código fuente del módulo de visualización (`visualization_module/`)

**En caso de querer probar la aplicación de demostración de la herramienta:**
- ChromaVision.exe (ejecutable del módulo de detección)
- Aplicación de demostración de prototipado de niveles


## Documentación

La documentación detallada (memoria del TFG y anexos) está disponible para descargar en un único archivo ZIP desde la [Release v1.0.0](https://github.com/ESPITY/TFG-ChromaVision/releases/tag/v1.0.0):
- Memoria - Desarrollo de una herramienta colaborativa con entorno físico interactivo y visualización 3D
- Anexo A - Especificaciones del sistema
- Anexo B - Módulo de detección
- Anexo C - Módulo de visualización (Unreal Engine)
- Anexo D - Aplicación de prototipado de niveles (Unreal Engine)
- Anexo E - Manual de usuario
- Anexo F - Manual de programador
