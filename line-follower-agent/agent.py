"""
Módulo: agent.py
Define la clase Agent, responsable de sensar, decidir y actuar según reglas.
"""
import json
from typing import Dict, Any, List, Tuple
from environment import Environment

class Rule:
    """
    Modela una regla con ID, condiciones y acciones.
    """
    def __init__(self, rule_id: str, conditions: Dict[str, Any], actions: List[str]):
        self.id = rule_id
        self.conditions = conditions
        self.actions = actions

    def matches(self, percep: Dict[str, Any]) -> bool:
        """
        Retorna True si todas las condiciones se cumplen en la percepción.
        """
        return all(percep.get(k) == v for k, v in self.conditions.items())

class Agent:
    """
    Agente reflexivo: sensa 5 valores y aplica reglas.

    Sensores:
      - contact: pared enfrente
      - under: celda bajo agente
      - above: celda diagonal enfrente-arriba
      - center: celda enfrente directa
      - below: celda diagonal enfrente-abajo
    """
    ORIENTS = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    MOVES = {'UP':(-1,0), 'RIGHT':(0,1), 'DOWN':(1,0), 'LEFT':(0,-1)}

    def __init__(self, env: Environment, rules: List[Rule], default_rule: Rule, start: Dict[str, Any]):
        self.env = env
        self.rules = rules
        self.default_rule = default_rule
        self.row = start.get('row', 1)
        self.col = start.get('col', 1)
        self.orientation = start.get('orientation', 'RIGHT')
        self.history: List[Dict[str, Any]] = []

    def sense(self) -> Dict[str, Any]:
        """
        Recoge percepción completa como dict.
        """
        ori = self.orientation
        dr, dc = self.MOVES[ori]
        contact = self.env.is_wall(self.row+dr, self.col+dc)
        under   = 'DARK' if self.env.is_dark(self.row, self.col) else 'CLEAR'
        idx = self.ORIENTS.index(ori)
        left_ori  = self.ORIENTS[(idx-1)%4]
        right_ori = self.ORIENTS[(idx+1)%4]
        # diagonales
        above = (self.row+dr+self.MOVES[left_ori][0], self.col+dc+self.MOVES[left_ori][1])
        center= (self.row+dr, self.col+dc)
        below = (self.row+dr+self.MOVES[right_ori][0], self.col+dc+self.MOVES[right_ori][1])
        def sense_cell(pos):
            r,c = pos
            if self.env.is_wall(r,c): return 'WALL'
            return 'DARK' if self.env.is_dark(r,c) else 'CLEAR'
        return {
            'contact': contact,
            'under': under,
            'above': sense_cell(above),
            'center': sense_cell(center),
            'below': sense_cell(below)
        }

    def decide(self, perception: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Selecciona la primera regla coincidente; o regla por defecto.
        """
        for rule in self.rules:
            if rule.matches(perception):
                return rule.id, rule.actions
        return self.default_rule.id, self.default_rule.actions

    def act(self, actions: List[str]) -> None:
        """
        Aplica acciones en secuencia: MOVE, ROTATE_LEFT, ROTATE_RIGHT.
        """
        for a in actions:
            if a == 'MOVE': self._move()
            elif a == 'ROTATE_LEFT': self._rotate(-1)
            elif a == 'ROTATE_RIGHT': self._rotate(1)

    def _move(self) -> None:
        dr, dc = self.MOVES[self.orientation]
        if not self.env.is_wall(self.row+dr, self.col+dc):
            self.row += dr; self.col += dc

    def _rotate(self, direction: int) -> None:
        idx = (self.ORIENTS.index(self.orientation)+direction)%4
        self.orientation = self.ORIENTS[idx]