import sympy as sp
import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class MultipleRootsMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, initial_guess, tolerance, max_iterations):
        """Método de Newton modificado para raíces múltiples"""
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

            # Validar ecuación
            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            expr = result['expression']
            x_sym = result['symbols']['x']

            # Calcular primera y segunda derivada
            f_prime = sp.diff(expr, x_sym)
            f_double_prime = sp.diff(f_prime, x_sym)

            f = result['numpy_function']
            f_p = sp.lambdify(x_sym, f_prime, modules=['numpy', 'math'])
            f_pp = sp.lambdify(x_sym, f_double_prime, modules=['numpy', 'math'])

            x = x0
            iterations = []

            for i in range(iter_val):
                fx = f(x)
                fpx = f_p(x)
                fppx = f_pp(x)

                denominator = fpx ** 2 - fx * fppx
                if abs(denominator) < 1e-15:
                    raise ValueError("Denominador cercano a cero")

                x_new = x - (fx * fpx) / denominator
                error = abs(x_new - x)

                iterations.append({
                    'Iteración': i + 1,
                    'x': x,
                    'f(x)': fx,
                    "f'(x)": fpx,
                    "f''(x)": fppx,
                    'x_new': x_new,
                    'Error': error
                })

                if error < tol_val:
                    break

                x = x_new

            # Estimar multiplicidad
            multiplicity = self.estimate_multiplicity(f, f_p, x_new)

            return {
                'success': True,
                'root': x_new,
                'iterations': iterations,
                'converged': error < tol_val,
                'final_error': error,
                'estimated_multiplicity': multiplicity,
                'function_calls': len(iterations) * 3,
                'first_derivative': sp.latex(f_prime),
                'second_derivative': sp.latex(f_double_prime),
                'message': 'Método completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'root': None,
                'iterations': []
            }

    def estimate_multiplicity(self, f, f_prime, root, h=1e-5):
        """Estima la multiplicidad de la raíz"""
        try:
            f_root = f(root)
            f_prime_root = f_prime(root)

            if abs(f_prime_root) < 1e-10:
                return 2
            else:
                return 1
        except:
            return 1