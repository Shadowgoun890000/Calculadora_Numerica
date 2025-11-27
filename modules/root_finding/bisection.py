import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator


class BisectionMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, a, b, tolerance, max_iterations):
        """Implementa el método de bisección"""
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

            # Parsear ecuación
            result = self.parser.parse_equation(equation_str, ['x'])
            f = result['numpy_function']

            # Verificar condiciones
            fa, fb = f(a_val), f(b_val)

            if fa * fb > 0:
                raise ValueError("La función debe cambiar de signo en el intervalo [a, b]")

            iterations = []
            a_current, b_current = a_val, b_val
            fa_current, fb_current = fa, fb

            for i in range(iter_val):
                c = (a_current + b_current) / 2
                fc = f(c)

                iterations.append({
                    'Iteración': i + 1,
                    'a': a_current,
                    'b': b_current,
                    'c': c,
                    'f(a)': fa_current,
                    'f(b)': fb_current,
                    'f(c)': fc,
                    'Error': abs(b_current - a_current) / 2
                })

                if abs(fc) < tol_val or (b_current - a_current) / 2 < tol_val:
                    break

                if fa_current * fc < 0:
                    b_current, fb_current = c, fc
                else:
                    a_current, fa_current = c, fc

            return {
                'success': True,
                'root': c,
                'iterations': iterations,
                'converged': abs(fc) < tol_val,
                'final_error': abs(b_current - a_current) / 2,
                'function_calls': len(iterations) + 2,  # f(a), f(b) inicial + f(c) en cada iteración
                'message': 'Método completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'root': None,
                'iterations': []
            }