import sympy as sp
import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator


class NewtonRaphsonMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, initial_guess, tolerance, max_iterations):
        """Implementa el método de Newton-Raphson"""
        try:
            # Validar entradas
            valid_guess, x0 = self.validator.validate_numeric_input(str(initial_guess))
            if not valid_guess:
                raise ValueError(f"Valor inicial inválido: {x0}")

            valid_tol, tol_val = self.validator.validate_numeric_input(str(tolerance), 1e-15, 1, True)
            if not valid_tol:
                raise ValueError(f"Tolerancia inválida: {tol_val}")

            valid_iter, iter_val = self.validator.validate_positive_integer(str(max_iterations), 1)
            if not valid_iter:
                raise ValueError(f"Iteraciones inválidas: {iter_val}")

            # Parsear ecuación
            result = self.parser.parse_equation(equation_str, ['x'])
            expr = result['expression']
            x_sym = result['symbols']['x']

            # Calcular derivada
            derivative = sp.diff(expr, x_sym)
            f_prime = sp.lambdify(x_sym, derivative, modules=['numpy', 'math'])
            f = result['numpy_function']

            x = x0
            iterations = []

            for i in range(iter_val):
                fx = f(x)
                fpx = f_prime(x)

                if abs(fpx) < 1e-15:
                    raise ValueError("Derivada cercana a cero. Posible punto estacionario.")

                x_new = x - fx / fpx
                error = abs(x_new - x)

                iterations.append({
                    'Iteración': i + 1,
                    'x': x,
                    'f(x)': fx,
                    "f'(x)": fpx,
                    'x_new': x_new,
                    'Error': error
                })

                if error < tol_val or abs(fx) < tol_val:
                    break

                x = x_new

            return {
                'success': True,
                'root': x_new,
                'iterations': iterations,
                'converged': error < tol_val,
                'final_error': error,
                'function_calls': len(iterations) * 2,  # f(x) y f'(x) en cada iteración
                'derivative_expression': sp.latex(derivative),
                'message': 'Método completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'root': None,
                'iterations': []
            }