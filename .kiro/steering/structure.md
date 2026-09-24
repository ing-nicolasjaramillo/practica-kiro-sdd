---
inclusion: always
---
# Estructura del proyecto

```
practica-kiro-sdd/
├── .kiro/steering/      Reglas permanentes
├── .kiro/specs/         Especificaciones (Kiro)
├── .opencode/agents/    Agentes de OpenCode
├── .opencode/skills/    Skills de OpenCode
├── src/validador/       Código de producción
├── tests/               Pruebas pytest
│   └── datos/           CSV y esquemas pequeños de prueba
├── datos/               Ejemplos para probar la CLI a mano
├── AGENTS.md
├── opencode.json
└── pyproject.toml
```

## Módulos esperados en src/validador/
- esquema.py: carga y valida el esquema JSON.
- lector.py: lee el CSV y entrega cabecera y filas numeradas.
- reglas.py: una función por regla; cada una devuelve lista de hallazgos.
- reporte.py: formatea hallazgos para consola y JSON.
- cli.py: argumentos, coordinación y códigos de salida.
- __main__.py: permite ejecutar python -m validador.

design.md puede refinar esta división, pero nunca mezclar lectura, reglas y
presentación en un mismo módulo.

## Reglas de ubicación
- Pruebas en tests/test_<modulo>.py, reflejando src/validador/.
- Ningún código fuera de src/ y tests/.
- Reportes generados por la CLI en reportes/ (ignorado por git).