import sympy as sp
import re
import numpy as np


class EquationParser:
    def __init__(self):
        self.supported_functions = {
            'sin': 'sin', 'cos': 'cos', 'tan': 'tan',
            'asin': 'asin', 'acos': 'acos', 'atan': 'atan',
            'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh',
            'exp': 'exp', 'log': 'log', 'ln': 'log',
            'sqrt': 'sqrt', 'abs': 'abs', 'pi': 'pi', 'e': 'e'
        }

    def parse_equation(self, equation_str, variables):
        """Convierte string de ecuación a función SymPy y numpy"""
        try:
            # Preprocesar la ecuación
            processed_eq = self.preprocess_equation(equation_str)

            # Crear símbolos
            symbols = {var: sp.Symbol(var) for var in variables}

            # Parsear ecuación
            expr = sp.sympify(processed_eq, locals=symbols)

            # Crear función numpy para evaluación numérica
            numpy_func = sp.lambdify(list(symbols.values()), expr, modules=['numpy', 'math'])

            # Crear función sympy para cálculos simbólicos
            sympy_func = lambda **kwargs: expr.subs(kwargs)

            return {
                'expression': expr,
                'numpy_function': numpy_func,
                'sympy_function': sympy_func,
                'symbols': symbols
            }

        except Exception as e:
            raise ValueError(f"Error al parsear ecuación: {str(e)}")

    def preprocess_equation(self, equation_str):
        """Preprocesa la ecuación para hacerla compatible con SymPy"""
        # Remover espacios
        equation_str = equation_str.replace(' ', '')

        # Reemplazar notaciones comunes
        replacements = {
            '^': '**',
            'ln': 'log',
        }

        for old, new in replacements.items():
            equation_str = equation_str.replace(old, new)

        # Agregar multiplicación implícita: 2x -> 2*x
        equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)
        equation_str = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', equation_str)
        equation_str = re.sub(r'\)([a-zA-Z])', r')*\1', equation_str)
        equation_str = re.sub(r'([a-zA-Z])\(', r'\1*(', equation_str)

        return equation_str

    def validate_equation(self, equation_str, variables):
        """Valida si la ecuación es correcta"""
        try:
            self.parse_equation(equation_str, variables)
            return True, "Ecuación válida"
        except Exception as e:
            return False, str(e)