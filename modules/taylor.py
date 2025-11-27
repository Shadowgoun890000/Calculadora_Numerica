import sympy as sp
from modules.equation_parser import EquationParser
from modules.validation import InputValidator

class TaylorPolynomial:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def expand(self, equation_str, variable, point, degree):
        """Calcula el polinomio de Taylor"""
        try:
            # Validar entradas
            valid_point, point_val = self.validator.validate_numeric_input(str(point))
            if not valid_point:
                raise ValueError(f"Punto de expansión inválido: {point_val}")

            valid_degree, degree_val = self.validator.validate_positive_integer(str(degree), 0)
            if not valid_degree:
                raise ValueError(f"Grado inválido: {degree_val}")

            valid_eq, msg = self.validator.validate_equation(equation_str, [variable])
            if not valid_eq:
                raise ValueError(msg)

            result = self.parser.parse_equation(equation_str, [variable])
            expr = result['expression']
            x = result['symbols'][variable]

            taylor_poly = 0
            derivatives = []
            derivative = None

            for n in range(degree_val + 1):
                if n == 0:
                    derivative = expr
                else:
                    derivative = sp.diff(derivative, x)

                derivative_at_point = derivative.subs(x, point_val)
                term = (derivative_at_point / sp.factorial(n)) * (x - point_val) ** n
                taylor_poly += term

                derivatives.append({
                    'order': n,
                    'derivative': sp.latex(derivative),
                    'value_at_point': float(derivative_at_point),
                    'term': sp.latex(term)
                })

            taylor_poly = sp.simplify(taylor_poly)
            taylor_func = sp.lambdify(x, taylor_poly, modules=['numpy', 'math'])

            return {
                'success': True,
                'original_function': equation_str,
                'expansion_point': point_val,
                'degree': degree_val,
                'taylor_polynomial': sp.latex(taylor_poly),
                'taylor_function': taylor_func,
                'derivatives': derivatives,
                'error_term': sp.latex(sp.Rational(1, sp.factorial(degree_val + 1)) *
                               sp.diff(expr, x, degree_val + 1).subs(x, sp.Symbol('ξ')) *
                               (x - point_val) ** (degree_val + 1)),
                'message': 'Polinomio de Taylor calculado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def approximate(self, equation_str, variable, point, degree, x_value):
        """Aproxima el valor de la función usando Taylor"""
        try:
            valid_x, x_val = self.validator.validate_numeric_input(str(x_value))
            if not valid_x:
                raise ValueError(f"Valor x inválido: {x_val}")

            result = self.expand(equation_str, variable, point, degree)
            if not result['success']:
                return result

            approximation = result['taylor_function'](x_val)
            original_result = self.parser.parse_equation(equation_str, [variable])
            real_value = original_result['numpy_function'](x_val)

            error = abs(real_value - approximation)

            return {
                'success': True,
                'approximation': approximation,
                'real_value': real_value,
                'absolute_error': error,
                'relative_error': error / abs(real_value) if real_value != 0 else float('inf'),
                'message': 'Aproximación calculada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }