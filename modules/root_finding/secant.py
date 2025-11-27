import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class SecantMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, x0, x1, tolerance, max_iterations):
        """Implementa el método de la secante"""
        try:
            # Validar entradas
            valid_x0, x0_val = self.validator.validate_numeric_input(str(x0))
            if not valid_x0:
                raise ValueError(f"x0 inválido: {x0_val}")

            valid_x1, x1_val = self.validator.validate_numeric_input(str(x1))
            if not valid_x1:
                raise ValueError(f"x1 inválido: {x1_val}")

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

            iterations = []
            x0_curr, x1_curr = x0_val, x1_val

            for i in range(iter_val):
                fx0, fx1 = f(x0_curr), f(x1_curr)

                if abs(fx1 - fx0) < 1e-15:
                    raise ValueError("Diferencia de función cercana a cero")

                x2 = x1_curr - fx1 * (x1_curr - x0_curr) / (fx1 - fx0)
                fx2 = f(x2)
                error = abs(x2 - x1_curr)

                iterations.append({
                    'Iteración': i + 1,
                    'x0': x0_curr,
                    'x1': x1_curr,
                    'x2': x2,
                    'f(x0)': fx0,
                    'f(x1)': fx1,
                    'f(x2)': fx2,
                    'Error': error
                })

                if error < tol_val or abs(fx2) < tol_val:
                    break

                x0_curr, x1_curr = x1_curr, x2

            return {
                'success': True,
                'root': x2,
                'iterations': iterations,
                'converged': error < tol_val,
                'final_error': error,
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