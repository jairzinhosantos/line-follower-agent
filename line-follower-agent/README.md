# Agente Seguidor de Líneas con Cobertura Completa de Casos

Este proyecto implementa un **agente reflexivo** en Python que recorre una malla 2D siguiendo “líneas” (celdas oscuras), detecta bucles y exporta resultados en JSON y Excel. La lógica de percepción→acción y los parámetros de simulación están completamente desacoplados en archivos JSON en la carpeta **input/**.

---

## Requisitos previos

1. Tener instalado Python 3.7+  
2. Git (o descargar el repositorio en ZIP)

---

## Instalación

1. **Clona el repositorio**  

```bash
git clone https://github.com/jairzinhosantos/line-follower-agent.git
cd line-follower-agent
```

2. **Crea y activa un entorno virtual (opcional pero recomendado)**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instala las dependencias**

```bash
pip install -r requirements.txt
```

## Estructura del proyecto

```bash
.
├── input/
│   ├── environment.json   # Parámetros de generación de la grilla
│   ├── rules.json         # 36 reglas + regla por defecto
│   └── simulation.json    # max_steps, seed, start, output_file
├── output/
│   ├── results.json       # Salida generada por runner.py
│   └── results.xlsx       # Excel generado por excel_generator.py
├── environment.py         # Clase Environment
├── agent.py               # Clases Rule y Agent
├── runner.py              # Carga inputs, simula y guarda JSON
├── excel_generator.py     # Convierte results.json a Excel
├── requirements.txt       # pandas, openpyxl
└── README.md              # Este documento
```

## Archivos de entrada (carpeta input/)

1. **environment.json**
Define cómo crear la malla:

```json
{
  "random": true,               
  "rows": 6,
  "cols": 8,
  "line_density": 0.15,
  "matrix": [                   // Solo si random=false
    [ -1, -1, -1, -1, -1, -1, -1, -1 ],
    [ -1,  0,  0,  0,  0,  0,  0, -1 ],
    …
    [ -1, -1, -1, -1, -1, -1, -1, -1 ]
  ]
}
```

- -1 = pared
- 1 = línea oscura
- 0 = celda clara

2. **rules.json**
Contiene 36 reglas numeradas y una regla por defecto (ID 37).
Cada regla especifica `id`, `conditions` (contact, under, center, above, below) y `actions` (MOVE, ROTATE_LEFT, ROTATE_RIGHT).


3. **simulation.json**
Parámetros de corrida:
```json
{
  "max_steps": 100,
  "seed": 42,
  "start": { "row": 1, "col": 1, "orientation": "RIGHT" },
  "output_file": "results.json"
}
```

## Descripción de módulos
### environment.py
- **Environment(params: dict)**
    - `_create_random(density)`: llena la grilla según line_density.
    - `_load_matrix(matrix)`: usa matriz fija.
    - `_add_walls()`: marca bordes como WALL.
    - `is_wall`, `is_dark`, `is_clear`: queries.
    - `display()`: imprime `#`/`X`/`espacio`.

### agent.py
- **Rule(id, conditions, actions)**
    - Verifica coincidencia entre `percep` y `conditions`.
- **Agent(env, rules, default_rule, start)**
    - `sense()`: devuelve dict con:
      - `contact`: pared al frente.
      - `under`: celda bajo el agente.
      - `above`: celda diagonal delante–arriba.
      - `center`: celda directamente delante.
      - `below`: celda diagonal delante–abajo.
    - `decide(percep)`: recorre reglas y devuelve `(rule_id, actions)`.
    - `act(actions)`: ejecuta `MOVE`, `ROTATE_LEFT`, `ROTATE_RIGHT`.
    - Guarda cada paso en history.

### runner.py
- **main():**
  1. Carga `input/environment.json`, `input/rules.json`, `input/simulation.json`.
  2. Fija semilla (`seed`) si existe.
  3. Instancia `Environment` y `Agent`.
  4. Imprime la grilla con `env.display()`.
  5. Bucle de hasta `max_steps`:
    - Detecta bucle (estado repetido) → sugiere heurística.
    - Sensa, decide, actúa y registra en `operation_table`.
  6. Genera `output/results.json` con:
    - `start`, `end`
    - `loop_detected`, `heuristic`
    - `matrix` (lista de listas)
    - `operation_table` (detalle por iteración)

### excel_generator.py
- Lee `output/results.json`.
- Usa pandas para crear `results.xlsx` con hojas:
  1. **Summary:** fila única con estados inicial/final y bucle.
  2. **Rules:** tabla de reglas de entrada.
  3. **Operations:** detalle de cada iteración (columnas: `iteration`, `orientation_start`, `pos_start_row`, …, `orientation_final`).
  4. **Matrix:** representación tabular de la matriz del entorno.

## Flujo de uso
1. Edita archivos en input/ según tus necesidades.
2. Ejecuta la simulación:
```bash
python runner.py
```
3. Opcionalmente, convierte la salida a Excel:
```bash
python excel_generator.py
```
4. Revisa los archivos generados:
- `output/results.json`: contiene toda la trazabilidad y la matriz.
- `results.xlsx`: versión legible en Excel.

## Heurística de bucle
- Un bucle ocurre si `(row, col, orientation)` se repite..
- Acción de salida: `ROTATE_RIGHT twice` y `reiniciar`.