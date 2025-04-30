"""
Módulo: environment.py
Define la clase Environment, responsable de generar y exponer el estado del entorno.
"""
import json
import random
from typing import Dict, Any, List

class Environment:
    """
    Representa la malla con celdas: paredes (-1), claras (0) y oscuras (1).
    Carga parámetros desde un dict (p.ej. parsed from input/environment.json).
    """
    WALL = -1
    CLEAR = 0
    DARK = 1

    def __init__(self, params: Dict[str, Any]):
        """
        Inicializa el entorno según parámetros:
        - random: bool
        - rows, cols: dimensiones
        - line_density: densidad de celdas oscuras (solo si random=true)
        - matrix: lista de listas (solo si random=false)
        """
        self.rows = params.get('rows', 10)
        self.cols = params.get('cols', 10)
        self.grid: List[List[int]] = []
        if params.get('random', True):
            self._create_random(params.get('line_density', 0.1))
        else:
            self._load_matrix(params.get('matrix', []))
        self._add_walls()

    def _create_random(self, density: float) -> None:
        """
        Genera una grilla vacía y asigna celdas DARK según densidad.
        """
        self.grid = [[self.CLEAR for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                self.grid[r][c] = self.DARK if random.random() < density else self.CLEAR

    def _load_matrix(self, matrix: List[List[int]]) -> None:
        """
        Carga una matriz predefinida de input/environment.json.
        """
        self.grid = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if self.rows > 0 else 0

    def _add_walls(self) -> None:
        """
        Marca bordes exteriores como paredes
        """
        for r in range(self.rows):
            self.grid[r][0] = self.WALL
            self.grid[r][self.cols-1] = self.WALL
        for c in range(self.cols):
            self.grid[0][c] = self.WALL
            self.grid[self.rows-1][c] = self.WALL

    def is_wall(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == self.WALL

    def is_dark(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == self.DARK

    def display(self) -> None:
        """
        Imprime la grilla en consola con símbolos:
        '#' pared, 'X' línea, ' ' celda clara
        """
        symbols = {self.WALL: '#', self.DARK: 'X', self.CLEAR: ' '}
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))