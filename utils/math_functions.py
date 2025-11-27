# utils/math_functions.py
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
        try:
            return np.linalg.cond(A)
        except np.linalg.LinAlgError:
            return float('inf')

    @staticmethod
    def is_positive_definite(A):
        """Verifica si una matriz es definida positiva"""
        try:
            # Verificar si es simétrica
            if not np.allclose(A, A.T):
                return False
            # Verificar si todos los eigenvalores son positivos
            eigenvalues = np.linalg.eigvals(A)
            return np.all(eigenvalues > 0)
        except:
            return False

    @staticmethod
    def is_diagonally_dominant(A):
        """Verifica si una matriz es diagonalmente dominante"""
        try:
            A_arr = np.array(A, dtype=float)
            n = A_arr.shape[0]

            for i in range(n):
                diagonal = abs(A_arr[i, i])
                row_sum = np.sum(np.abs(A_arr[i, :])) - diagonal
                if diagonal <= row_sum:
                    return False
            return True
        except:
            return False

    @staticmethod
    def derivative(f, x, h=1e-5):
        """Calcula la derivada numérica de una función"""
        return (f(x + h) - f(x - h)) / (2 * h)

    @staticmethod
    def second_derivative(f, x, h=1e-5):
        """Calcula la segunda derivada numérica"""
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h ** 2)

    @staticmethod
    def polynomial_degree(coefficients):
        """Determina el grado efectivo de un polinomio"""
        # Eliminar ceros al final para encontrar el grado real
        coeffs = np.array(coefficients)
        for i in range(len(coeffs) - 1, -1, -1):
            if abs(coeffs[i]) > 1e-10:
                return i
        return 0

    @staticmethod
    def validate_matrix_dimensions(A, b):
        """Valida que las dimensiones de A y b sean compatientes"""
        A_arr = np.array(A)
        b_arr = np.array(b)

        if A_arr.ndim != 2:
            return False, "A debe ser una matriz 2D"

        if b_arr.ndim != 1:
            return False, "b debe ser un vector 1D"

        if A_arr.shape[0] != b_arr.shape[0]:
            return False, f"Dimensiones incompatibles: A {A_arr.shape}, b {b_arr.shape}"

        return True, "Dimensiones válidas"

    @staticmethod
    def compute_residual(A, x, b):
        """Calcula el residual de un sistema lineal"""
        try:
            A_arr = np.array(A, dtype=float)
            x_arr = np.array(x, dtype=float)
            b_arr = np.array(b, dtype=float)
            return np.linalg.norm(np.dot(A_arr, x_arr) - b_arr)
        except:
            return float('inf')