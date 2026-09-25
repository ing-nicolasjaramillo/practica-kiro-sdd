# AGENTS.md — validador-csv

Proyecto en Spec Driven Development. Fuentes de verdad, en orden:
1. .kiro/steering/*.md: producto, tecnología y estructura.
2. .kiro/specs/validador-csv/: requirements.md, design.md, tasks.md.

## Reglas para todo agente
- No implementes nada que no esté en tasks.md. Si falta algo, repórtalo.
- Una tarea a la vez, en el orden de tasks.md.
- Todo cambio de código lleva prueba (skill python-tdd).
- Nunca modifiques requirements.md ni design.md. Ante una contradicción, detente y repórtala.
- No hagas commit ni push; los hace el humano.

## Definición de terminado de una tarea
- Pruebas nuevas en verde, con nombres test_req_<n>_<m>_<caso>.
- Suite completa en verde.
- El revisor respondió APROBADO.
- Tarea marcada [x] en tasks.md.