import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class GaussianQuadrature:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()
        self.gauss_data = {
            2: {
                'nodes': [-0.5773502691896257, 0.5773502691896257],
                'weights': [1.0, 1.0]
            },
            3: {
                'nodes': [-0.7745966692414834, 0.0, 0.7745966692414834],
                'weights': [0.5555555555555556, 0.8888888888888888, 0.5555555555555556]
            },
            4: {
                'nodes': [-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526],
                'weights': [0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538]
            },
            5: {
                'nodes': [-0.9061798459386640, -0.5384693101056831, 0.0, 0.5384693101056831, 0.9061798459386640],
                'weights': [0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665,
                            0.2369268850561891]
            }
        }

    def solve(self, equation_str, a, b, n_points):
        """Cuadratura de Gauss-Legendre"""
        try:
            # Validar entradas
            valid_interval, (a_val, b_val) = self.validator.validate_interval(str(a), str(b))
            if not valid_interval:
                raise ValueError(f"Intervalo inválido: {a_val}")

            valid_points, points_val = self.validator.validate_positive_integer(str(n_points), 2)
            if not valid_points:
                raise ValueError(f"Número de puntos inválido: {points_val}")

            if points_val not in self.gauss_data:
                raise ValueError(f"Número de puntos no soportado: {points_val}")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            nodes = self.gauss_data[points_val]['nodes']
            weights = self.gauss_data[points_val]['weights']

            mapped_nodes = [0.5 * (b_val - a_val) * xi + 0.5 * (a_val + b_val) for xi in nodes]

            integral = 0
            for i in range(points_val):
                integral += weights[i] * f(mapped_nodes[i])

            integral *= 0.5 * (b_val - a_val)

            return {
                'success': True,
                'integral': integral,
                'method': f'Gauss-Legendre ({points_val} puntos)',
                'nodes': list(zip(mapped_nodes, f(np.array(mapped_nodes)))),
                'original_nodes': nodes,
                'weights': weights,
                'function_evaluations': points_val,
                'error_estimate': self.estimate_error(f, a_val, b_val, points_val),
                'message': 'Integral calculada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def estimate_error(self, f, a, b, n_points):
        """Estimación simplificada del error"""
        return abs((b - a) ** (2 * n_points + 1) / (2 * n_points + 1))