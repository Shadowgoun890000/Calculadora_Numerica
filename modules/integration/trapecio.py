import numpy as np
from modules.equation_parser import EquationParser


class TrapezoidalRule:
    def __init__(self):
        self.parser = EquationParser()

    def solve(self, equation_str, a, b, n):
        """Regla del trapecio compuesta"""
        try:
            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b - a) / n
            x = np.linspace(a, b, n + 1)
            y = f(x)

            # Aplicar regla del trapecio
            integral = y[0] + y[-1]
            integral += 2 * np.sum(y[1:-1])
            integral *= h / 2

            # Estimación del error
            error_estimate = abs((b - a) * h ** 2 / 12)  # Estimación conservadora

            return {
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Trapecio Compuesto',
                'intervals': n,
                'step_size': h,
                'error_estimate': error_estimate,
                'function_evaluations': n + 1
            }

        except Exception as e:
            raise ValueError(f"Error en regla del trapecio: {str(e)}")