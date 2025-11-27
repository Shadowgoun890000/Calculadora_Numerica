import numpy as np
import sympy as sp


class ResultFormatter:
    @staticmethod
    def format_number(x, precision=6, scientific_threshold=1e-4):
        """Formatea números para display"""
        if x is None:
            return "N/A"

        if isinstance(x, (int, np.integer)):
            return str(x)

        if abs(x) < 1e-15:
            return "0"

        if abs(x) > 1 / scientific_threshold or (abs(x) < scientific_threshold and x != 0):
            return f"{x:.{precision}e}"
        else:
            return f"{x:.{precision}f}"

    @staticmethod
    def format_matrix(matrix, precision=4, max_rows=10, max_cols=10):
        """Formatea matrices para display"""
        if matrix is None:
            return "N/A"

        matrix = np.array(matrix)
        if matrix.ndim == 1:
            matrix = matrix.reshape(1, -1)

        rows, cols = matrix.shape

        # Limitar tamaño para display
        display_rows = min(rows, max_rows)
        display_cols = min(cols, max_cols)

        formatted = []
        for i in range(display_rows):
            row_str = "  ".join([ResultFormatter.format_number(matrix[i, j], precision)
                                 for j in range(display_cols)])
            if cols > max_cols:
                row_str += "  ..."
            formatted.append(f"[ {row_str} ]")

        if rows > max_rows:
            formatted.append("...")

        return "\n".join(formatted)

    @staticmethod
    def format_iteration_table(iterations, headers):
        """Formatea tabla de iteraciones"""
        if not iterations:
            return "No hay iteraciones para mostrar"

        # Determinar ancho de columnas
        col_widths = []
        for header in headers:
            col_widths.append(len(header))

        for iteration in iterations:
            for i, header in enumerate(headers):
                value = iteration.get(header, '')
                if isinstance(value, (int, float)):
                    value_str = ResultFormatter.format_number(value)
                else:
                    value_str = str(value)
                col_widths[i] = max(col_widths[i], len(value_str))

        # Construir tabla
        table = []

        # Encabezados
        header_row = " | ".join([header.ljust(col_widths[i]) for i, header in enumerate(headers)])
        table.append(header_row)
        table.append("-" * len(header_row))

        # Filas de datos
        for iteration in iterations:
            row = []
            for i, header in enumerate(headers):
                value = iteration.get(header, '')
                if isinstance(value, (int, float)):
                    value_str = ResultFormatter.format_number(value)
                else:
                    value_str = str(value)
                row.append(value_str.ljust(col_widths[i]))
            table.append(" | ".join(row))

        return "\n".join(table)

    @staticmethod
    def format_latex(expr):
        """Formatea expresión LaTeX"""
        try:
            if hasattr(expr, '__len__') and not isinstance(expr, str):
                return "\\begin{bmatrix}\n" + " \\\\\n".join(
                    " & ".join(ResultFormatter.format_number(x) for x in row)
                    for row in expr
                ) + "\n\\end{bmatrix}"
            else:
                return str(expr)
        except:
            return str(expr)

    @staticmethod
    def format_error_message(error):
        """Formatea mensajes de error"""
        if "division by zero" in str(error).lower():
            return "Error: División por cero"
        elif "singular" in str(error).lower():
            return "Error: Matriz singular o mal condicionada"
        elif "converge" in str(error).lower():
            return "Error: El método no converge"
        else:
            return f"Error: {str(error)}"