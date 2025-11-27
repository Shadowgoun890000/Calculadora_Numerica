import numpy as np


class JacobiMethod:
    def solve(self, A, b, initial_guess=None, tolerance=1e-6, max_iterations=1000):
        """Resuelve Ax = b usando el método de Jacobi"""
        try:
            A = np.array(A, dtype=float)
            b = np.array(b, dtype=float)

            n = len(b)

            if initial_guess is None:
                x = np.zeros(n)
            else:
                x = np.array(initial_guess, dtype=float)

            # Verificar que A sea diagonal dominante
            if not self.is_diagonally_dominant(A):
                return {
                    'success': False,
                    'error': 'La matriz no es diagonalmente dominante. La convergencia no está garantizada.'
                }

            iterations = []
            for k in range(max_iterations):
                x_new = np.zeros_like(x)

                for i in range(n):
                    sigma = 0
                    for j in range(n):
                        if j != i:
                            sigma += A[i, j] * x[j]
                    x_new[i] = (b[i] - sigma) / A[i, i]

                error = np.linalg.norm(x_new - x, ord=np.inf)
                residual = np.linalg.norm(np.dot(A, x_new) - b, ord=np.inf)

                iterations.append({
                    'iteration': k + 1,
                    'x': x_new.copy(),
                    'error': error,
                    'residual': residual
                })

                if error < tolerance:
                    break

                x = x_new

            return {
                'success': True,
                'solution': x_new,
                'iterations': iterations,
                'converged': error < tolerance,
                'final_error': error,
                'final_residual': residual,
                'iterations_count': len(iterations)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error en método de Jacobi: {str(e)}"
            }

    def is_diagonally_dominant(self, A):
        """Verifica si la matriz es diagonalmente dominante"""
        n = A.shape[0]
        for i in range(n):
            row_sum = np.sum(np.abs(A[i, :])) - np.abs(A[i, i])
            if np.abs(A[i, i]) <= row_sum:
                return False
        return True