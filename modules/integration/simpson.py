import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class SimpsonIntegration:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def simpson_13(self, equation_str, a, b, n):
        """Regla de Simpson 1/3 compuesta"""
        try:
            valid_interval, (a_val, b_val) = self.validator.validate_interval(str(a), str(b))
            if not valid_interval:
                raise ValueError(f"Intervalo inválido: {a_val}")

            valid_n, n_val = self.validator.validate_positive_integer(str(n), 2)
            if not valid_n:
                raise ValueError(f"Número de intervalos inválido: {n_val}")

            if n_val % 2 != 0:
                raise ValueError("n debe ser par para Simpson 1/3")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b_val - a_val) / n_val
            x = np.linspace(a_val, b_val, n_val + 1)
            y = f(x)

            integral = y[0] + y[-1]
            integral += 4 * np.sum(y[1:-1:2])
            integral += 2 * np.sum(y[2:-2:2])
            integral *= h / 3

            error_estimate = self.estimate_error(f, a_val, b_val, n_val, '1/3')

            return {
                'success': True,
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Simpson 1/3',
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

    def simpson_38(self, equation_str, a, b, n):
        """Regla de Simpson 3/8 compuesta"""
        try:
            valid_interval, (a_val, b_val) = self.validator.validate_interval(str(a), str(b))
            if not valid_interval:
                raise ValueError(f"Intervalo inválido: {a_val}")

            valid_n, n_val = self.validator.validate_positive_integer(str(n), 3)
            if not valid_n:
                raise ValueError(f"Número de intervalos inválido: {n_val}")

            if n_val % 3 != 0:
                raise ValueError("n debe ser múltiplo de 3 para Simpson 3/8")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b_val - a_val) / n_val
            x = np.linspace(a_val, b_val, n_val + 1)
            y = f(x)

            integral = y[0] + y[-1]
            indices_3 = [i for i in range(1, n_val) if i % 3 != 0]
            integral += 3 * np.sum(y[indices_3])
            indices_2 = [i for i in range(3, n_val - 1, 3)]
            integral += 2 * np.sum(y[indices_2])
            integral *= 3 * h / 8

            error_estimate = self.estimate_error(f, a_val, b_val, n_val, '3/8')

            return {
                'success': True,
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Simpson 3/8',
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

    def estimate_error(self, f, a, b, n, method):
        h = (b - a) / n
        if method == '1/3':
            return abs((b - a) * h ** 4 / 180)
        else:
            return abs((b - a) * h ** 4 / 80)