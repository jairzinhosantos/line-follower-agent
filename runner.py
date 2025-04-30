"""
Script principal: carga inputs, ejecuta simulación y genera output/result.json
"""
import json
import random
from pathlib import Path
from environment import Environment
from agent import Agent, Rule

# Directorios
INPUT_DIR  = Path('input')
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

def load_json(fname: str):
    path = INPUT_DIR / fname
    with open(path, 'r') as f:
        return json.load(f)

def main():
    # Cargar parámetros
    env_params = load_json('environment.json')
    rules_data = load_json('rules.json')
    sim_params = load_json('simulation.json')

    # Semilla y entorno
    if 'seed' in sim_params:
        random.seed(sim_params['seed'])
    env = Environment(env_params)

    # Construir lista de Rule
    rules = [Rule(r['id'], r['conditions'], r['actions']) for r in rules_data['rules']]
    default = Rule(rules_data['default_rule']['id'], {}, rules_data['default_rule']['actions'])

    # Instanciar agente
    agent = Agent(env, rules, default, sim_params['start'])

    # Mostrar matriz inicial
    print("Environment:")
    env.display()

    seen = set()
    loop = False
    heuristic = None

    # Ejecución iterativa
    for i in range(sim_params.get('max_steps', 1000)):
        state = (agent.row, agent.col, agent.orientation)
        if state in seen:
            loop = True
            heuristic = 'ROTATE_RIGHT twice'
            break
        seen.add(state)

        percep = agent.sense()
        rid, actions = agent.decide(percep)
        agent.act(actions)

        # Registrar en historial
        agent.history.append({
            'iteration': i,
            'pos_start_row': state[0],
            'pos_start_col': state[1],
            'orientation_start': state[2],
            **percep,
            'rule_id': rid,
            'actions': actions,
            'pos_final_row': agent.row,
            'pos_final_col': agent.col,
            'orientation_final': agent.orientation
        })

    # Resultado
    result = {
        'start': sim_params['start'],
        'end': {
            'row': agent.row, 'col': agent.col,
            'orientation': agent.orientation
        },
        'loop_detected': loop,
        'heuristic': heuristic,
        'matrix': env.grid,
        'operation_table': agent.history
    }

    # Guardar JSON
    out_path = OUTPUT_DIR / sim_params.get('output_file', 'results.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Result saved to {out_path}")

if __name__ == '__main__':
    main()