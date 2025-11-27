# utils/formatters.py
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
        error_str = str(error).lower()
        if "division by zero" in error_str:
            return "Error: División por cero"
        elif "singular" in error_str:
            return "Error: Matriz singular o mal condicionada"
        elif "converge" in error_str:
            return "Error: El método no converge"
        elif "root" in error_str and "found" not in error_str:
            return "Error: No se pudo encontrar la raíz"
        elif "invalid" in error_str:
            return "Error: Entrada inválida"
        elif "dimension" in error_str:
            return "Error: Dimensiones incorrectas"
        else:
            # Acortar mensajes de error muy largos
            if len(error_str) > 100:
                return f"Error: {error_str[:100]}..."
            return f"Error: {str(error)}"

    @staticmethod
    def format_method_result(result, method_name):
        """Formatea el resultado completo de un método numérico"""
        if not result.get('success', False):
            error_msg = ResultFormatter.format_error_message(result.get('error', 'Error desconocido'))
            return {
                'success': False,
                'error': error_msg,
                'formatted_output': f"**{method_name}**\n\n{error_msg}"
            }

        output_lines = [f"**{method_name}**", ""]

        # Información básica del método
        if 'root' in result:
            output_lines.append(f"**Raíz encontrada:** {ResultFormatter.format_number(result['root'])}")

        if 'integral' in result:
            output_lines.append(f"**Valor de la integral:** {ResultFormatter.format_number(result['integral'])}")

        if 'solution' in result:
            if isinstance(result['solution'], (list, np.ndarray)):
                output_lines.append(f"**Solución:** {ResultFormatter.format_matrix(result['solution'])}")
            else:
                output_lines.append(f"**Solución:** {ResultFormatter.format_number(result['solution'])}")

        # Métricas de convergencia
        if 'converged' in result:
            status = "✓ Convergió" if result['converged'] else "✖ No convergió"
            output_lines.append(f"**Estado:** {status}")

        if 'final_error' in result:
            output_lines.append(f"**Error final:** {ResultFormatter.format_number(result['final_error'])}")

        if 'iterations_count' in result:
            output_lines.append(f"**Iteraciones:** {result['iterations_count']}")

        if 'function_calls' in result:
            output_lines.append(f"**Evaluaciones de función:** {result['function_calls']}")

        # Información adicional específica del método
        if 'estimated_multiplicity' in result:
            output_lines.append(f"**Multiplicidad estimada:** {result['estimated_multiplicity']}")

        if 'error_estimate' in result:
            output_lines.append(f"**Error estimado:** {ResultFormatter.format_number(result['error_estimate'])}")

        if 'message' in result:
            output_lines.append(f"**Mensaje:** {result['message']}")

        # Tabla de iteraciones si existe
        if 'iterations' in result and result['iterations']:
            output_lines.append("\n**Tabla de Iteraciones:**")
            headers = list(result['iterations'][0].keys())
            iteration_table = ResultFormatter.format_iteration_table(result['iterations'], headers)
            output_lines.append(f"```\n{iteration_table}\n```")

        # Pasos de eliminación si existen
        if 'steps' in result and result['steps']:
            output_lines.append("\n**Pasos del método:**")
            for i, step in enumerate(result['steps']):
                output_lines.append(f"\n**Paso {i + 1}:** {step.get('description', '')}")
                if 'matrix' in step:
                    output_lines.append(f"```\n{ResultFormatter.format_matrix(step['matrix'])}\n```")

        return {
            'success': True,
            'formatted_output': "\n".join(output_lines),
            'raw_result': result
        }