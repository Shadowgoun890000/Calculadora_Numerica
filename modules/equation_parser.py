import sympy as sp
import numpy as np
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)


class EquationParser:
    def __init__(self):
        self.supported_functions = {
            "sin": "sin",
            "cos": "cos",
            "tan": "tan",
            "asin": "asin",
            "acos": "acos",
            "atan": "atan",
            "sinh": "sinh",
            "cosh": "cosh",
            "tanh": "tanh",
            "exp": "exp",
            "log": "log",
            "ln": "log",
            "sqrt": "sqrt",
            "abs": "abs",
            "pi": "pi",
            "e": "E",  # e de Euler
        }

    def parse_equation(self, equation_str, variables):
        """Convierte string de ecuación a función SymPy y numpy"""
        try:
            # 1) Preprocesar (reemplazos de símbolos)
            processed_eq = self.preprocess_equation(equation_str)

            # 2) Crear símbolos
            symbols = {var: sp.Symbol(var) for var in variables}

            # 3) Diccionario local: funciones + constantes + variables
            local_dict = {}
            for name, sym_name in self.supported_functions.items():
                if hasattr(sp, sym_name):
                    local_dict[name] = getattr(sp, sym_name)
            local_dict.update(symbols)

            # 4) Activar multiplicación implícita: 2x, 3(x+1), xsin(x), etc.
            transformations = standard_transformations + (
                implicit_multiplication_application,
            )

            expr = parse_expr(
                processed_eq,
                local_dict=local_dict,
                transformations=transformations,
            )

            # 5) Función numpy para evaluación numérica
            numpy_func = sp.lambdify(
                list(symbols.values()), expr, modules=["numpy", "math"]
            )

            # 6) Función sympy para cálculos simbólicos
            sympy_func = lambda **kwargs: expr.subs(kwargs)

            return {
                "expression": expr,
                "numpy_function": numpy_func,
                "sympy_function": sympy_func,
                "symbols": symbols,
            }

        except Exception as e:
            raise ValueError(f"Error al parsear ecuación: {str(e)}")

    def preprocess_equation(self, equation_str):
        """Preprocesa la ecuación para hacerla compatible con SymPy."""
        if equation_str is None:
            return ""

        # Quitar espacios
        equation_str = equation_str.replace(" ", "")

        # Reemplazar símbolos bonitos por sintaxis SymPy
        replacements = {
            "^": "**",      # potencia visual
            "√": "sqrt",    # raíz
            "π": "pi",      # pi
            "÷": "/",       # si algún día pones ÷
            "×": "*",       # si usas × en vez de *
            "ln": "log",    # log natural
        }

        for old, new in replacements.items():
            equation_str = equation_str.replace(old, new)

        return equation_str

    def validate_equation(self, equation_str, variables):
        """Valida si la ecuación es correcta."""
        try:
            self.parse_equation(equation_str, variables)
            return True, "Ecuación válida"
        except Exception as e:
            return False, str(e)