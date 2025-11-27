import re
import numpy as np
from modules.equation_parser import EquationParser


class InputValidator:
    def __init__(self):
        self.parser = EquationParser()

    def validate_equation(self, equation_str, required_variables=['x']):
        """Valida que la ecuación sea sintácticamente correcta"""
        if not equation_str or equation_str.strip() == "":
            return False, "La ecuación no puede estar vacía"

        try:
            # Intentar parsear la ecuación
            self.parser.parse_equation(equation_str, required_variables)
            return True, "Ecuación válida"
        except Exception as e:
            return False, f"Error en la ecuación: {str(e)}"

    def validate_numeric_input(self, value_str, min_val=None, max_val=None, allow_negative=True):
        """Valida una entrada numérica"""
        try:
            value = float(value_str)

            if not allow_negative and value < 0:
                return False, "El valor no puede ser negativo"

            if min_val is not None and value < min_val:
                return False, f"El valor debe ser mayor o igual a {min_val}"

            if max_val is not None and value > max_val:
                return False, f"El valor debe ser menor o igual a {max_val}"

            return True, value
        except ValueError:
            return False, "Por favor ingrese un número válido"

    def validate_interval(self, a_str, b_str):
        """Valida que [a, b] sea un intervalo válido"""
        valid_a, a = self.validate_numeric_input(a_str)
        if not valid_a:
            return False, f"Valor de 'a' inválido: {a}"

        valid_b, b = self.validate_numeric_input(b_str)
        if not valid_b:
            return False, f"Valor de 'b' inválido: {b}"

        if a >= b:
            return False, "El valor de 'a' debe ser menor que 'b'"

        return True, (a, b)

    def validate_positive_integer(self, value_str, min_val=1):
        """Valida que sea un entero positivo"""
        try:
            value = int(value_str)
            if value < min_val:
                return False, f"El valor debe ser mayor o igual a {min_val}"
            return True, value
        except ValueError:
            return False, "Por favor ingrese un número entero válido"

    def validate_matrix(self, matrix_str, rows, cols):
        """Valida una matriz ingresada como string"""
        try:
            # Convertir string a matriz numpy
            rows_list = matrix_str.strip().split('\n')
            if len(rows_list) != rows:
                return False, f"Se esperaban {rows} filas"

            matrix = []
            for i, row_str in enumerate(rows_list):
                elements = row_str.strip().split()
                if len(elements) != cols:
                    return False, f"Fila {i + 1}: se esperaban {cols} elementos"

                row = []
                for j, elem in enumerate(elements):
                    valid, value = self.validate_numeric_input(elem)
                    if not valid:
                        return False, f"Elemento [{i + 1},{j + 1}]: {value}"
                    row.append(value)
                matrix.append(row)

            return True, np.array(matrix)
        except Exception as e:
            return False, f"Error al procesar la matriz: {str(e)}"

    def validate_vector(self, vector_str, size):
        """Valida un vector ingresado como string"""
        try:
            elements = vector_str.strip().split()
            if len(elements) != size:
                return False, f"Se esperaban {size} elementos"

            vector = []
            for i, elem in enumerate(elements):
                valid, value = self.validate_numeric_input(elem)
                if not valid:
                    return False, f"Elemento {i + 1}: {value}"
                vector.append(value)

            return True, np.array(vector)
        except Exception as e:
            return False, f"Error al procesar el vector: {str(e)}"