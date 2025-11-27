import numpy as np


class GaussSeidelMethod:
    def solve(self, A, b, initial_guess=None, tolerance=1e-6, max_iterations=1000):
        """Resuelve Ax = b usando el método de Gauss-Seidel"""
        try:
            A = np.array(A, dtype=float)
            b = np.array(b, dtype=float)

            n = len(b)

            if initial_guess is None:
                x = np.zeros(n)
            else:
                x = np.array(initial_guess, dtype=float)

            iterations = []
            for k in range(max_iterations):
                x_old = x.copy()

                for i in range(n):
                    sigma1 = np.dot(A[i, :i], x[:i])
                    sigma2 = np.dot(A[i, i + 1:], x_old[i + 1:])
                    x[i] = (b[i] - sigma1 - sigma2) / A[i, i]

                error = np.linalg.norm(x - x_old, ord=np.inf)
                residual = np.linalg.norm(np.dot(A, x) - b, ord=np.inf)

                iterations.append({
                    'iteration': k + 1,
                    'x': x.copy(),
                    'error': error,
                    'residual': residual
                })

                if error < tolerance:
                    break

            return {
                'success': True,
                'solution': x,
                'iterations': iterations,
                'converged': error < tolerance,
                'final_error': error,
                'final_residual': residual,
                'iterations_count': len(iterations)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error en método de Gauss-Seidel: {str(e)}"
            }