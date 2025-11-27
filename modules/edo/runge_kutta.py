import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class RungeKuttaMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, y0, t0, tf, h, order=4):
        """Método de Runge-Kutta"""
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

            if order not in [2, 4]:
                raise ValueError("El orden debe ser 2 o 4")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['t', 'y'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            t = np.arange(t0_val, tf_val + h_val, h_val)
            n = len(t)
            y = np.zeros(n)
            y[0] = y0_val

            if order == 4:
                return self.rk4(f, t, y, h_val, n)
            else:
                return self.rk2(f, t, y, h_val, n)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def rk4(self, f, t, y, h, n):
        for i in range(n - 1):
            k1 = h * f(t[i], y[i])
            k2 = h * f(t[i] + h / 2, y[i] + k1 / 2)
            k3 = h * f(t[i] + h / 2, y[i] + k2 / 2)
            k4 = h * f(t[i] + h, y[i] + k3)
            y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6

        return {
            'success': True,
            't': t,
            'y': y,
            'method': 'Runge-Kutta 4to Orden',
            'step_size': h,
            'steps': n - 1,
            'points': list(zip(t, y)),
            'local_truncation_error': h ** 5,
            'global_truncation_error': h ** 4,
            'message': 'Método completado exitosamente'
        }

    def rk2(self, f, t, y, h, n):
        for i in range(n - 1):
            k1 = h * f(t[i], y[i])
            k2 = h * f(t[i] + h / 2, y[i] + k1 / 2)
            y[i + 1] = y[i] + k2

        return {
            'success': True,
            't': t,
            'y': y,
            'method': 'Runge-Kutta 2do Orden',
            'step_size': h,
            'steps': n - 1,
            'points': list(zip(t, y)),
            'local_truncation_error': h ** 3,
            'global_truncation_error': h ** 2,
            'message': 'Método completado exitosamente'
        }