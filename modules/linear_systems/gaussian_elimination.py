import numpy as np
import copy


class GaussianElimination:
    def __init__(self):
        self.steps = []

    def solve(self, A, b, pivot_type='partial'):
        """Resuelve Ax = b usando eliminación gaussiana"""
        try:
            A = np.array(A, dtype=float)
            b = np.array(b, dtype=float)

            n = len(b)

            # Matriz aumentada
            Ab = np.hstack([A, b.reshape(-1, 1)])
            self.steps = [{'matrix': Ab.copy(), 'description': 'Matriz inicial'}]

            # Eliminación hacia adelante
            for i in range(n):
                # Pivoteo
                if pivot_type == 'partial':
                    Ab = self.partial_pivot(Ab, i)
                elif pivot_type == 'total':
                    Ab = self.total_pivot(Ab, i)

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de pivoteo en fila {i + 1}'
                })

                # Verificar pivote cero
                if abs(Ab[i, i]) < 1e-10:
                    return {
                        'success': False,
                        'error': 'Sistema singular o mal condicionado'
                    }

                # Eliminación
                for j in range(i + 1, n):
                    factor = Ab[j, i] / Ab[i, i]
                    Ab[j, i:] = Ab[j, i:] - factor * Ab[i, i:]

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de eliminación en columna {i + 1}'
                })

            # Sustitución hacia atrás
            x = np.zeros(n)
            for i in range(n - 1, -1, -1):
                x[i] = (Ab[i, -1] - np.dot(Ab[i, i + 1:n], x[i + 1:])) / Ab[i, i]

            # Verificar solución
            residual = np.linalg.norm(np.dot(A, x) - b)

            return {
                'success': True,
                'solution': x,
                'steps': self.steps,
                'residual': residual,
                'matrix_triangular': Ab[:, :-1],
                'vector_transformed': Ab[:, -1]
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error en eliminación gaussiana: {str(e)}"
            }

    def partial_pivot(self, Ab, col):
        """Pivoteo parcial"""
        n = Ab.shape[0]
        max_row = np.argmax(np.abs(Ab[col:, col])) + col

        if max_row != col:
            Ab[[col, max_row]] = Ab[[max_row, col]]

        return Ab

    def total_pivot(self, Ab, start):
        """Pivoteo total"""
        n = Ab.shape[0]
        # Encontrar el elemento con mayor valor absoluto en la submatriz
        submatrix = Ab[start:, start:-1]
        max_index = np.unravel_index(np.argmax(np.abs(submatrix)), submatrix.shape)
        max_row, max_col = max_index[0] + start, max_index[1] + start

        if max_row != start:
            Ab[[start, max_row]] = Ab[[max_row, start]]
        if max_col != start:
            Ab[:, [start, max_col]] = Ab[:, [max_col, start]]
            # Guardar información del intercambio de columnas

        return Ab


class GaussJordanElimination(GaussianElimination):
    def solve(self, A, b, pivot_type='partial'):
        """Resuelve Ax = b usando eliminación de Gauss-Jordan"""
        try:
            A = np.array(A, dtype=float)
            b = np.array(b, dtype=float)

            n = len(b)
            Ab = np.hstack([A, b.reshape(-1, 1)])
            self.steps = [{'matrix': Ab.copy(), 'description': 'Matriz inicial'}]

            for i in range(n):
                # Pivoteo
                if pivot_type == 'partial':
                    Ab = self.partial_pivot(Ab, i)

                # Hacer el pivote 1
                pivot = Ab[i, i]
                Ab[i, :] = Ab[i, :] / pivot

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Pivote {i + 1} normalizado a 1'
                })

                # Eliminar en todas las otras filas
                for j in range(n):
                    if j != i:
                        factor = Ab[j, i]
                        Ab[j, :] = Ab[j, :] - factor * Ab[i, :]

                self.steps.append({
                    'matrix': Ab.copy(),
                    'description': f'Después de eliminar columna {i + 1}'
                })

            x = Ab[:, -1]
            residual = np.linalg.norm(np.dot(A, x) - b)

            return {
                'success': True,
                'solution': x,
                'steps': self.steps,
                'residual': residual,
                'matrix_identity': Ab[:, :-1],
                'vector_solution': Ab[:, -1]
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error en Gauss-Jordan: {str(e)}"
            }