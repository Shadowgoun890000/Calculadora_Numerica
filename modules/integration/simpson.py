import numpy as np
from modules.equation_parser import EquationParser


class SimpsonIntegration:
    def __init__(self):
        self.parser = EquationParser()

    def simpson_13(self, equation_str, a, b, n):
        """Regla de Simpson 1/3 compuesta"""
        try:
            if n % 2 != 0:
                raise ValueError("n debe ser par para Simpson 1/3")

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b - a) / n
            x = np.linspace(a, b, n + 1)
            y = f(x)

            # Aplicar regla de Simpson 1/3
            integral = y[0] + y[-1]
            integral += 4 * np.sum(y[1:-1:2])  # Términos impares
            integral += 2 * np.sum(y[2:-2:2])  # Términos pares
            integral *= h / 3

            # Calcular error estimado
            error_estimate = self.estimate_error(f, a, b, n, '1/3')

            return {
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Simpson 1/3',
                'intervals': n,
                'step_size': h,
                'error_estimate': error_estimate,
                'function_evaluations': n + 1
            }

        except Exception as e:
            raise ValueError(f"Error en Simpson 1/3: {str(e)}")

    def simpson_38(self, equation_str, a, b, n):
        """Regla de Simpson 3/8 compuesta"""
        try:
            if n % 3 != 0:
                raise ValueError("n debe ser múltiplo de 3 para Simpson 3/8")

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            h = (b - a) / n
            x = np.linspace(a, b, n + 1)
            y = f(x)

            # Aplicar regla de Simpson 3/8
            integral = y[0] + y[-1]

            # Términos con coeficiente 3
            indices_3 = [i for i in range(1, n) if i % 3 != 0]
            integral += 3 * np.sum(y[indices_3])

            # Términos con coeficiente 2
            indices_2 = [i for i in range(3, n - 1, 3)]
            integral += 2 * np.sum(y[indices_2])

            integral *= 3 * h / 8

            error_estimate = self.estimate_error(f, a, b, n, '3/8')

            return {
                'integral': integral,
                'points': list(zip(x, y)),
                'method': 'Simpson 3/8',
                'intervals': n,
                'step_size': h,
                'error_estimate': error_estimate,
                'function_evaluations': n + 1
            }

        except Exception as e:
            raise ValueError(f"Error en Simpson 3/8: {str(e)}")

    def estimate_error(self, f, a, b, n, method):
        """Estima el error de truncamiento"""
        # Esta es una estimación simplificada
        h = (b - a) / n

        if method == '1/3':
            # Error de Simpson 1/3: -(b-a)h⁴f⁽⁴⁾(ξ)/180
            return abs((b - a) * h ** 4 / 180)  # Estimación conservadora
        else:  # 3/8
            # Error de Simpson 3/8: -(b-a)h⁴f⁽⁴⁾(ξ)/80
            return abs((b - a) * h ** 4 / 80)