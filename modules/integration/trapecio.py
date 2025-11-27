import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class TrapezoidalRule:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, a, b, n):
        """Regla del trapecio compuesta"""
        try:
            # Validar entradas
            valid_interval, (a_val, b_val) = self.validator.validate_interval(str(a), str(b))
            if not valid_interval:
                raise ValueError(f"Intervalo inválido: {a_val}")

            valid_n, n_val = self.validator.validate_positive_integer(str(n), 1)
            if not valid_n:
                raise ValueError(f"Número de intervalos inválido: {n_val}")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b_val - a_val) / n_val
            x = np.linspace(a_val, b_val, n_val + 1)
            y = f(x)

            integral = y[0] + y[-1]
            integral += 2 * np.sum(y[1:-1])
            integral *= h / 2

            error_estimate = abs((b_val - a_val) * h ** 2 / 12)

            return {
                'success': True,
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Trapecio Compuesto',
                'intervals': n_val,
                'step_size': h,
                'error_estimate': error_estimate,
                'function_evaluations': n_val + 1,
                'message': 'Integral calculada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }