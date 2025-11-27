import numpy as np
from modules.validation import InputValidator

class GaussianElimination:
    def __init__(self):
        self.steps = []
        self.validator = InputValidator()

    def solve(self, A, b, pivot_type='partial'):
        """Resuelve Ax = b usando eliminación gaussiana"""
        try:
            if not isinstance(A, (list, np.ndarray)) or not isinstance(b, (list, np.ndarray)):
                raise ValueError("A y b deben ser listas o arrays numpy")

            A_arr = np.array(A, dtype=float)
            b_arr = np.array(b, dtype=float)

            n = len(b_arr)

            if A_arr.shape != (n, n):
                raise ValueError("La matriz A debe ser cuadrada y coincidir con el tamaño de b")

            Ab = np.hstack([A_arr, b_arr.reshape(-1, 1)])
            self.steps = [{'matrix': Ab.copy(), 'description': 'Matriz inicial'}]

            for i in range(n):
                if pivot_type == 'partial':
                    Ab = self.partial_pivot(Ab, i)
                elif pivot_type == 'total':
                    Ab = self.total_pivot(Ab, i)

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de pivoteo en fila {i + 1}'
                })

                if abs(Ab[i, i]) < 1e-10:
                    return {
                        'success': False,
                        'error': 'Sistema singular o mal condicionado'
                    }

                for j in range(i + 1, n):
                    factor = Ab[j, i] / Ab[i, i]
                    Ab[j, i:] = Ab[j, i:] - factor * Ab[i, i:]

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de eliminación en columna {i + 1}'
                })

            x = np.zeros(n)
            for i in range(n - 1, -1, -1):
                x[i] = (Ab[i, -1] - np.dot(Ab[i, i + 1:n], x[i + 1:])) / Ab[i, i]

            residual = np.linalg.norm(np.dot(A_arr, x) - b_arr)

            return {
                'success': True,
                'solution': x,
                'steps': self.steps,
                'residual': residual,
                'matrix_triangular': Ab[:, :-1],
                'vector_transformed': Ab[:, -1],
                'message': 'Eliminación gaussiana completada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def partial_pivot(self, Ab, col):
        n = Ab.shape[0]
        max_row = np.argmax(np.abs(Ab[col:, col])) + col

        if max_row != col:
            Ab[[col, max_row]] = Ab[[max_row, col]]

        return Ab

    def total_pivot(self, Ab, start):
        n = Ab.shape[0]
        submatrix = Ab[start:, start:-1]
        max_index = np.unravel_index(np.argmax(np.abs(submatrix)), submatrix.shape)
        max_row, max_col = max_index[0] + start, max_index[1] + start

        if max_row != start:
            Ab[[start, max_row]] = Ab[[max_row, start]]
        if max_col != start:
            Ab[:, [start, max_col]] = Ab[:, [max_col, start]]

        return Ab

class GaussJordanElimination(GaussianElimination):
    def solve(self, A, b, pivot_type='partial'):
        """Resuelve Ax = b usando eliminación de Gauss-Jordan"""
        try:
            if not isinstance(A, (list, np.ndarray)) or not isinstance(b, (list, np.ndarray)):
                raise ValueError("A y b deben ser listas o arrays numpy")

            A_arr = np.array(A, dtype=float)
            b_arr = np.array(b, dtype=float)

            n = len(b_arr)

            if A_arr.shape != (n, n):
                raise ValueError("La matriz A debe ser cuadrada y coincidir con el tamaño de b")

            Ab = np.hstack([A_arr, b_arr.reshape(-1, 1)])
            self.steps = [{'matrix': Ab.copy(), 'description': 'Matriz inicial'}]

            for i in range(n):
                if pivot_type == 'partial':
                    Ab = self.partial_pivot(Ab, i)

                pivot = Ab[i, i]
                Ab[i, :] = Ab[i, :] / pivot

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Pivote {i + 1} normalizado a 1'
                })

                for j in range(n):
                    if j != i:
                        factor = Ab[j, i]
                        Ab[j, :] = Ab[j, :] - factor * Ab[i, :]

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de eliminar columna {i + 1}'
                })

            x = Ab[:, -1]
            residual = np.linalg.norm(np.dot(A_arr, x) - b_arr)

            return {
                'success': True,
                'solution': x,
                'steps': self.steps,
                'residual': residual,
                'matrix_identity': Ab[:, :-1],
                'vector_solution': Ab[:, -1],
                'message': 'Eliminación Gauss-Jordan completada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }