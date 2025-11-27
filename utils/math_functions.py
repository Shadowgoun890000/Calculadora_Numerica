import numpy as np
import sympy as sp


class MathUtils:
    @staticmethod
    def factorial(n):
        """Factorial para números enteros grandes"""
        if n < 0:
            raise ValueError("Factorial no definido para números negativos")
        return np.math.factorial(n) if n < 20 else sp.factorial(n)

    @staticmethod
    def relative_error(true_value, approx_value):
        """Error relativo porcentual"""
        if true_value == 0:
            return float('inf') if approx_value != 0 else 0
        return abs((true_value - approx_value) / true_value) * 100

    @staticmethod
    def absolute_error(true_value, approx_value):
        """Error absoluto"""
        return abs(true_value - approx_value)

    @staticmethod
    def condition_number(A):
        """Número de condición de una matriz"""
        return np.linalg.cond(A)

    @staticmethod
    def is_positive_definite(A):
        """Verifica si una matriz es definida positiva"""
        try:
            np.linalg.cholesky(A)
            return True
        except np.linalg.LinAlgError:
            return False


# utils/formatters.py
def format_number(x, precision=6):
    """Formatea números para display"""
    if x is None:
        return "N/A"

    if isinstance(x, (int, np.integer)):
        return str(x)

    if abs(x) < 1e-10:
        return "0"

    if abs(x) > 1e6 or abs(x) < 1e-6:
        return f"{x:.{precision}e}"
    else:
        return f"{x:.{precision}f}"


def format_matrix(matrix, precision=4):
    """Formatea matrices para display"""
    if matrix is None:
        return "N/A"

    matrix = np.array(matrix)
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)

    rows = []
    for row in matrix:
        row_str = "[" + "  ".join([format_number(x, precision) for x in row]) + "]"
        rows.append(row_str)

    return "\n".join(rows)


def format_iteration_table(iterations, headers):
    """Formatea tabla de iteraciones"""
    table = []

    # Encabezados
    header_row = " | ".join(headers)
    table.append(header_row)
    table.append("-" * len(header_row))

    # Filas de datos
    for iter in iterations:
        row = " | ".join([format_number(iter.get(col, '')) for col in headers])
        table.append(row)

    return "\n".join(table)