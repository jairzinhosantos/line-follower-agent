import json
from pathlib import Path
import pandas as pd

"""
excel_generator.py

Convierte output/result.json y input/rules.json en un Excel con varias hojas:
- Summary: estados inicial y final, detección de bucle y heurística
- Rules: tabla de reglas de entrada (incluye regla por defecto)
- Operations: detalle de cada iteración
- Matrix: representación tabular de la grilla
"""

# Rutas de archivos
INPUT_RESULT = Path('output') / 'results.json'
INPUT_RULES = Path('input') / 'rules.json'
OUTPUT_EXCEL = Path('output') / 'results.xlsx'

def load_json(path: Path) -> dict:
    """Carga un archivo JSON y retorna su contenido."""
    with open(path, 'r') as f:
        return json.load(f)

def build_summary_df(result: dict) -> pd.DataFrame:
    """Construye un DataFrame resumen con estado inicial, final y bucle."""
    start = result['start']
    end = result['end']
    return pd.DataFrame([{
        'start_row': start['row'],
        'start_col': start['col'],
        'start_orientation': start['orientation'],
        'end_row': end['row'],
        'end_col': end['col'],
        'end_orientation': end['orientation'],
        'loop_detected': result['loop_detected'],
        'heuristic': result.get('heuristic')
    }])

def build_rules_df() -> pd.DataFrame:
    """Construye un DataFrame con todas las reglas de input/rules.json."""
    rules_data = load_json(INPUT_RULES)
    rules = rules_data.get('rules', [])
    default = rules_data.get('default_rule', {})
    all_rules = rules + [default]
    return pd.json_normalize(all_rules)

def build_operations_df(result: dict) -> pd.DataFrame:
    """Construye un DataFrame con la tabla de operaciones (iteraciones)."""
    return pd.json_normalize(result['operation_table'])

def build_matrix_df(result: dict) -> pd.DataFrame:
    """Construye un DataFrame con la matriz del entorno."""
    return pd.DataFrame(result['matrix'])

def main():
    # Carga datos
    result = load_json(INPUT_RESULT)
    
    # Construir DataFrames
    summary_df = build_summary_df(result)
    rules_df = build_rules_df()
    ops_df = build_operations_df(result)
    matrix_df = build_matrix_df(result)
    
    # Escribir a Excel
    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        rules_df.to_excel(writer, sheet_name='Rules', index=False)
        ops_df.to_excel(writer, sheet_name='Operations', index=False)
        matrix_df.to_excel(writer, sheet_name='Matrix', index=False)
    
    print(f"Excel generado: {OUTPUT_EXCEL}")

if __name__ == '__main__':
    main()