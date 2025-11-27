import numpy as np
from modules.equation_parser import EquationParser


class GaussianQuadrature:
    def __init__(self):
        self.parser = EquationParser()
        # Pesos y nodos para cuadratura de Gauss-Legendre
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
            if n_points not in self.gauss_data:
                raise ValueError(f"Número de puntos no soportado: {n_points}")

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            nodes = self.gauss_data[n_points]['nodes']
            weights = self.gauss_data[n_points]['weights']

            # Mapear de [-1,1] a [a,b]
            mapped_nodes = [0.5 * (b - a) * xi + 0.5 * (a + b) for xi in nodes]

            # Calcular integral
            integral = 0
            for i in range(n_points):
                integral += weights[i] * f(mapped_nodes[i])

            integral *= 0.5 * (b - a)

            return {
                'integral': integral,
                'method': f'Gauss-Legendre ({n_points} puntos)',
                'nodes': list(zip(mapped_nodes, f(np.array(mapped_nodes)))),
                'original_nodes': nodes,
                'weights': weights,
                'function_evaluations': n_points,
                'error_estimate': self.estimate_error(f, a, b, n_points)
            }

        except Exception as e:
            raise ValueError(f"Error en cuadratura de Gauss: {str(e)}")

    def estimate_error(self, f, a, b, n_points):
        """Estimación simplificada del error"""
        # Para Gauss-Legendre, el error es proporcional a f^(2n)(ξ)
        return abs((b - a) ** (2 * n_points + 1) / (2 * n_points + 1))