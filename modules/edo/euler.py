import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class EulerMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, y0, t0, tf, h):
        """Método de Euler para EDOs"""
        try:
            # Validar entradas
            valid_y0, y0_val = self.validator.validate_numeric_input(str(y0))
            if not valid_y0:
                raise ValueError(f"y0 inválido: {y0_val}")

            valid_t0, t0_val = self.validator.validate_numeric_input(str(t0))
            if not valid_t0:
                raise ValueError(f"t0 inválido: {t0_val}")

            valid_tf, tf_val = self.validator.validate_numeric_input(str(tf))
            if not valid_tf:
                raise ValueError(f"tf inválido: {tf_val}")

            valid_h, h_val = self.validator.validate_numeric_input(str(h), 1e-10, None, True)
            if not valid_h:
                raise ValueError(f"h inválido: {h_val}")

            if tf_val <= t0_val:
                raise ValueError("tf debe ser mayor que t0")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['t', 'y'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            t = np.arange(t0_val, tf_val + h_val, h_val)
            n = len(t)
            y = np.zeros(n)
            y[0] = y0_val

            for i in range(n - 1):
                y[i + 1] = y[i] + h_val * f(t[i], y[i])

            return {
                'success': True,
                't': t,
                'y': y,
                'method': 'Euler',
                'step_size': h_val,
                'steps': n - 1,
                'points': list(zip(t, y)),
                'message': 'Método de Euler completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }