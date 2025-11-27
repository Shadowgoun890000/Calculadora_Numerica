import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class FalsePositionMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, a, b, tolerance, max_iterations):
        """Implementa el método de falsa posición"""
        try:
            # Validar entradas
            valid_interval, (a_val, b_val) = self.validator.validate_interval(str(a), str(b))
            if not valid_interval:
                raise ValueError(f"Intervalo inválido: {a_val}")

            valid_tol, tol_val = self.validator.validate_numeric_input(str(tolerance), 1e-15, 1, True)
            if not valid_tol:
                raise ValueError(f"Tolerancia inválida: {tol_val}")

            valid_iter, iter_val = self.validator.validate_positive_integer(str(max_iterations), 1)
            if not valid_iter:
                raise ValueError(f"Iteraciones inválidas: {iter_val}")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['x'])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            fa, fb = f(a_val), f(b_val)

            if fa * fb > 0:
                raise ValueError("La función debe cambiar de signo en el intervalo [a, b]")

            iterations = []
            a_curr, b_curr = a_val, b_val
            fa_curr, fb_curr = fa, fb

            for i in range(iter_val):
                c = (a_curr * fb_curr - b_curr * fa_curr) / (fb_curr - fa_curr)
                fc = f(c)

                iterations.append({
                    'Iteración': i + 1,
                    'a': a_curr,
                    'b': b_curr,
                    'c': c,
                    'f(a)': fa_curr,
                    'f(b)': fb_curr,
                    'f(c)': fc,
                    'Error': abs(fc)
                })

                if abs(fc) < tol_val:
                    break

                if fa_curr * fc < 0:
                    b_curr, fb_curr = c, fc
                else:
                    a_curr, fa_curr = c, fc

            return {
                'success': True,
                'root': c,
                'iterations': iterations,
                'converged': abs(fc) < tol_val,
                'final_error': abs(fc),
                'function_calls': len(iterations) * 3,
                'message': 'Método completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'root': None,
                'iterations': []
            }