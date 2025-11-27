import numpy as np
from modules.validation import InputValidator

class GaussSeidelMethod:
    def __init__(self):
        self.validator = InputValidator()

    def solve(self, A, b, initial_guess=None, tolerance=1e-6, max_iterations=1000):
        """Resuelve Ax = b usando el método de Gauss-Seidel"""
        try:
            # Validar matriz y vector
            if not isinstance(A, (list, np.ndarray)) or not isinstance(b, (list, np.ndarray)):
                raise ValueError("A y b deben ser listas o arrays numpy")

            A_arr = np.array(A, dtype=float)
            b_arr = np.array(b, dtype=float)

            n = len(b_arr)

            if A_arr.shape != (n, n):
                raise ValueError("La matriz A debe ser cuadrada y coincidir con el tamaño de b")

            # Validar parámetros numéricos
            valid_tol, tol_val = self.validator.validate_numeric_input(str(tolerance), 1e-15, 1, True)
            if not valid_tol:
                raise ValueError(f"Tolerancia inválida: {tol_val}")

            valid_iter, iter_val = self.validator.validate_positive_integer(str(max_iterations), 1)
            if not valid_iter:
                raise ValueError(f"Iteraciones inválidas: {iter_val}")

            if initial_guess is None:
                x = np.zeros(n)
            else:
                if len(initial_guess) != n:
                    raise ValueError("El vector inicial debe tener el mismo tamaño que b")
                x = np.array(initial_guess, dtype=float)

            iterations = []
            for k in range(iter_val):
                x_old = x.copy()

                for i in range(n):
                    sigma1 = np.dot(A_arr[i, :i], x[:i])
                    sigma2 = np.dot(A_arr[i, i + 1:], x_old[i + 1:])
                    x[i] = (b_arr[i] - sigma1 - sigma2) / A_arr[i, i]

                error = np.linalg.norm(x - x_old, ord=np.inf)
                residual = np.linalg.norm(np.dot(A_arr, x) - b_arr, ord=np.inf)

                iterations.append({
                    'Iteración': k + 1,
                    'x': x.copy(),
                    'Error': error,
                    'Residual': residual
                })

                if error < tol_val:
                    break

            return {
                'success': True,
                'solution': x,
                'iterations': iterations,
                'converged': error < tol_val,
                'final_error': error,
                'final_residual': residual,
                'iterations_count': len(iterations),
                'message': 'Método completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }