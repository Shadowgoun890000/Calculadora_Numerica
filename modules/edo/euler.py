import numpy as np
from modules.equation_parser import EquationParser


class EulerMethod:
    def __init__(self):
        self.parser = EquationParser()

    def solve(self, equation_str, y0, t0, tf, h):
        """Método de Euler para EDOs"""
        try:
            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            # Crear arreglo de tiempo
            t = np.arange(t0, tf + h, h)
            n = len(t)

            # Inicializar solución
            y = np.zeros(n)
            y[0] = y0

            # Aplicar método de Euler
            for i in range(n - 1):
                y[i + 1] = y[i] + h * f(t[i], y[i])

            return {
                't': t,
                'y': y,
                'method': 'Euler',
                'step_size': h,
                'steps': n - 1,
                'points': list(zip(t, y))
            }

        except Exception as e:
            raise ValueError(f"Error en método de Euler: {str(e)}")