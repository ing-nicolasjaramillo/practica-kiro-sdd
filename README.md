# Laboratorio SDD: validador-csv

Práctica de Spec Driven Development.
- Kiro genera la especificación (.kiro/specs).
- OpenCode la ejecuta con agentes y skills (.opencode).

## Uso
python -m validador datos/ventas_valido.csv --esquema datos/esquema_ventas.json

## Pruebas
python -m pytest


¿Cómo trabaja opencode y kiro?
Desde opencode.json en 'instructions' es donde se hace que OpenCode lea los mismos archivos de steering que Kiro. Esta es la pieza que une las dos herramientas. 