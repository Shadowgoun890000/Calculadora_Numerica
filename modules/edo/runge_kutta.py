import numpy as np
from modules.equation_parser import EquationParser


class RungeKuttaMethod:
    def __init__(self):
        self.parser = EquationParser()

    def solve(self, equation_str, y0, t0, tf, h, order=4):
        """Método de Runge-Kutta de 4to orden"""
        try:
            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            t = np.arange(t0, tf + h, h)
            n = len(t)
            y = np.zeros(n)
            y[0] = y0

            if order == 4:
                return self.rk4(f, t, y, h, n)
            elif order == 2:
                return self.rk2(f, t, y, h, n)
            else:
                raise ValueError("Solo se soportan órdenes 2 y 4")

        except Exception as e:
            raise ValueError(f"Error en método de Runge-Kutta: {str(e)}")

    def rk4(self, f, t, y, h, n):
        """Runge-Kutta de 4to orden"""
        for i in range(n - 1):
            k1 = h * f(t[i], y[i])
            k2 = h * f(t[i] + h / 2, y[i] + k1 / 2)
            k3 = h * f(t[i] + h / 2, y[i] + k2 / 2)
            k4 = h * f(t[i] + h, y[i] + k3)

            y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6

        return {
            't': t,
            'y': y,
            'method': 'Runge-Kutta 4to Orden',
            'step_size': h,
            'steps': n - 1,
            'points': list(zip(t, y)),
            'local_truncation_error': h ** 5,  # Error local de truncamiento
            'global_truncation_error': h ** 4  # Error global
        }

    def rk2(self, f, t, y, h, n):
        """Runge-Kutta de 2do orden (método del punto medio)"""
        for i in range(n - 1):
            k1 = h * f(t[i], y[i])
            k2 = h * f(t[i] + h / 2, y[i] + k1 / 2)

            y[i + 1] = y[i] + k2

        return {
            't': t,
            'y': y,
            'method': 'Runge-Kutta 2do Orden',
            'step_size': h,
            'steps': n - 1,
            'points': list(zip(t, y)),
            'local_truncation_error': h ** 3,
            'global_truncation_error': h ** 2
        }