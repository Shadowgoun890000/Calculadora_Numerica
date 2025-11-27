# modules/ode/euler_modified.py
import numpy as np
from modules.equation_parser import EquationParser
from modules.validation import InputValidator


class ModifiedEulerMethod:
    def __init__(self):
        self.parser = EquationParser()
        self.validator = InputValidator()

    def solve(self, equation_str, y0, t0, tf, h):
        """Método de Euler modificado (Heun) para EDOs"""
        try:
            # Validar entradas
            valid_y0, y0_val = self.validator.validate_numeric_input(str(y0))
            if not valid_y0:
                raise ValueError(f"y0 inválido: {y0_val}")

            valid_t0, t0_val = self.validator.validate_numeric_input(str(t0))
            if not valid_t0:
                raise ValueError(f"t0 inválido: {t0_val}")

            valid_tf, tf_val = self.validator.validate_numeric_input(str(tf))
            if not valid_tf:
                raise ValueError(f"tf inválido: {tf_val}")

            valid_h, h_val = self.validator.validate_numeric_input(str(h), 1e-10, None, True)
            if not valid_h:
                raise ValueError(f"h inválido: {h_val}")

            if tf_val <= t0_val:
                raise ValueError("tf debe ser mayor que t0")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['t', 'y'])
            if not valid_eq:
                raise ValueError(msg)

            # Parsear ecuación
            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            # Crear arreglo de tiempo
            t = np.arange(t0_val, tf_val + h_val, h_val)
            n = len(t)

            # Inicializar solución
            y = np.zeros(n)
            y[0] = y0_val

            # Almacenar información de cada paso
            steps_info = []

            # Aplicar método de Euler modificado
            for i in range(n - 1):
                # Paso 1: Euler simple (predictor)
                k1 = h_val * f(t[i], y[i])
                y_pred = y[i] + k1

                # Paso 2: Corrector usando el promedio de pendientes
                k2 = h_val * f(t[i] + h_val, y_pred)
                y[i + 1] = y[i] + 0.5 * (k1 + k2)

                # Guardar información del paso
                steps_info.append({
                    'step': i + 1,
                    't': t[i],
                    'y': y[i],
                    'k1': k1,
                    'y_pred': y_pred,
                    'k2': k2,
                    'y_new': y[i + 1],
                    'local_error': self.estimate_local_error(f, t[i], y[i], h_val)
                })

            # Calcular errores estimados
            local_error = h_val ** 3  # Error local de truncamiento O(h³)
            global_error = h_val ** 2  # Error global O(h²)

            return {
                'success': True,
                't': t,
                'y': y,
                'method': 'Euler Modificado (Heun)',
                'step_size': h_val,
                'steps': n - 1,
                'points': list(zip(t, y)),
                'steps_info': steps_info,
                'local_truncation_error': local_error,
                'global_truncation_error': global_error,
                'final_value': y[-1],
                'function_evaluations': (n - 1) * 2,  # 2 evaluaciones por paso
                'message': 'Método de Euler modificado completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def estimate_local_error(self, f, t, y, h):
        """Estima el error local usando comparación con método de orden superior"""
        try:
            # Método de Euler simple
            euler_step = y + h * f(t, y)

            # Método de Euler modificado (ya calculado)
            k1 = h * f(t, y)
            k2 = h * f(t + h, y + k1)
            heun_step = y + 0.5 * (k1 + k2)

            # Diferencia como estimación del error
            return abs(heun_step - euler_step)
        except:
            return 0.0

    def solve_adaptive(self, equation_str, y0, t0, tf, h0, tolerance=1e-6, max_steps=1000):
        """Versión adaptativa del método de Euler modificado"""
        try:
            # Validar entradas
            valid_y0, y0_val = self.validator.validate_numeric_input(str(y0))
            if not valid_y0:
                raise ValueError(f"y0 inválido: {y0_val}")

            valid_t0, t0_val = self.validator.validate_numeric_input(str(t0))
            if not valid_t0:
                raise ValueError(f"t0 inválido: {t0_val}")

            valid_tf, tf_val = self.validator.validate_numeric_input(str(tf))
            if not valid_tf:
                raise ValueError(f"tf inválido: {tf_val}")

            valid_h, h_val = self.validator.validate_numeric_input(str(h0), 1e-10, None, True)
            if not valid_h:
                raise ValueError(f"h0 inválido: {h_val}")

            valid_tol, tol_val = self.validator.validate_numeric_input(str(tolerance), 1e-12, 1, True)
            if not valid_tol:
                raise ValueError(f"Tolerancia inválida: {tol_val}")

            valid_max_steps, max_steps_val = self.validator.validate_positive_integer(str(max_steps), 1)
            if not valid_max_steps:
                raise ValueError(f"Máximo de pasos inválido: {max_steps_val}")

            if tf_val <= t0_val:
                raise ValueError("tf debe ser mayor que t0")

            valid_eq, msg = self.validator.validate_equation(equation_str, ['t', 'y'])
            if not valid_eq:
                raise ValueError(msg)

            # Parsear ecuación
            result = self.parser.parse_equation(equation_str, ['t', 'y'])
            f = result['numpy_function']

            # Inicializar arrays
            t_list = [t0_val]
            y_list = [y0_val]
            h_list = [h_val]
            error_list = [0.0]

            steps_info = []
            current_t = t0_val
            current_y = y0_val
            current_h = h_val
            step_count = 0

            while current_t < tf_val and step_count < max_steps_val:
                # Paso con el tamaño actual
                k1 = current_h * f(current_t, current_y)
                y_pred = current_y + k1
                k2 = current_h * f(current_t + current_h, y_pred)
                y_new = current_y + 0.5 * (k1 + k2)

                # Estimar error
                error_est = self.estimate_local_error(f, current_t, current_y, current_h)

                # Control adaptativo del tamaño de paso
                if error_est > tol_val and current_h > 1e-8:
                    # Reducir tamaño de paso si el error es muy grande
                    current_h *= 0.5
                    continue
                elif error_est < tol_val * 0.1 and current_h < (tf_val - t0_val) / 10:
                    # Aumentar tamaño de paso si el error es muy pequeño
                    current_h *= 1.5

                # Aceptar paso
                current_t += current_h
                current_y = y_new

                t_list.append(current_t)
                y_list.append(current_y)
                h_list.append(current_h)
                error_list.append(error_est)

                steps_info.append({
                    'step': step_count + 1,
                    't': current_t,
                    'y': current_y,
                    'h': current_h,
                    'error_estimate': error_est,
                    'accepted': True
                })

                step_count += 1

                # Asegurarse de no pasar tf
                if current_t + current_h > tf_val:
                    current_h = tf_val - current_t

            return {
                'success': True,
                't': np.array(t_list),
                'y': np.array(y_list),
                'method': 'Euler Modificado Adaptativo',
                'step_sizes': np.array(h_list),
                'error_estimates': np.array(error_list),
                'steps': step_count,
                'points': list(zip(t_list, y_list)),
                'steps_info': steps_info,
                'final_value': current_y,
                'function_evaluations': step_count * 2,
                'adaptive': True,
                'message': 'Método de Euler modificado adaptativo completado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def compare_with_euler(self, equation_str, y0, t0, tf, h):
        """Compara Euler modificado con Euler simple"""
        try:
            # Calcular con Euler modificado
            result_modified = self.solve(equation_str, y0, t0, tf, h)

            if not result_modified['success']:
                return result_modified

            # Calcular con Euler simple para comparación
            from .euler import EulerMethod
            euler_method = EulerMethod()
            result_euler = euler_method.solve(equation_str, y0, t0, tf, h)

            if not result_euler['success']:
                return result_modified  # Retornar solo el resultado del método modificado

            # Calcular diferencias
            t_modified = result_modified['t']
            y_modified = result_modified['y']
            y_euler = result_euler['y']

            differences = np.abs(y_modified - y_euler)
            max_difference = np.max(differences)
            avg_difference = np.mean(differences)

            # Agregar información de comparación al resultado
            result_modified['comparison'] = {
                'euler_solution': y_euler,
                'differences': differences,
                'max_difference': max_difference,
                'avg_difference': avg_difference,
                'improvement_ratio': avg_difference / (np.mean(np.abs(y_euler)) + 1e-10)
            }

            result_modified['message'] += f"\nComparación: Diferencia máxima con Euler simple = {max_difference:.6f}"

            return result_modified

        except Exception as e:
            # Si falla la comparación, retornar solo el resultado del método modificado
            if 'result_modified' in locals() and result_modified['success']:
                result_modified['comparison_error'] = str(e)
                return result_modified
            else:
                return {
                    'success': False,
                    'error': f"Error en comparación: {str(e)}"
                }