import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots


class InteractivePlotter:
    def __init__(self):
        self.colors = px.colors.qualitative.Set1

    def plot_root_finding(self, equation_data, root_data, x_range=(-10, 10)):
        """Gráfica interactiva para métodos de búsqueda de raíces"""
        try:
            # Crear puntos para la función
            x = np.linspace(x_range[0], x_range[1], 1000)
            y = equation_data['numpy_function'](x)

            fig = go.Figure()

            # Graficar función
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name='f(x)',
                line=dict(color=self.colors[0], width=2)
            ))

            # Graficar raíz encontrada
            if root_data.get('root') is not None:
                fig.add_trace(go.Scatter(
                    x=[root_data['root']], y=[0],
                    mode='markers',
                    name='Raíz',
                    marker=dict(color='red', size=10, symbol='x')
                ))

            # Graficar iteraciones si están disponibles
            if root_data.get('iterations'):
                iterations = root_data['iterations']
                iter_points = []

                for iter in iterations:
                    if 'c' in iter:  # Bisección, falsa posición
                        iter_points.append((iter['c'], 0))
                    elif 'x_new' in iter:  # Newton, secante
                        iter_points.append((iter['x_new'], 0))

                if iter_points:
                    iter_x, iter_y = zip(*iter_points)
                    fig.add_trace(go.Scatter(
                        x=iter_x, y=iter_y,
                        mode='markers+lines',
                        name='Iteraciones',
                        marker=dict(color='orange', size=6),
                        line=dict(dash='dot')
                    ))

            # Línea y=0
            fig.add_hline(y=0, line_dash="dash", line_color="gray")

            fig.update_layout(
                title="Método de Búsqueda de Raíces",
                xaxis_title="x",
                yaxis_title="f(x)",
                hovermode='closest'
            )

            return fig

        except Exception as e:
            # Gráfica de error en caso de problema
            fig = go.Figure()
            fig.add_annotation(text=f"Error al generar gráfica: {str(e)}",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False)
            return fig

    def plot_integration(self, equation_data, integration_data, a, b):
        """Gráfica interactiva para métodos de integración"""
        try:
            # Crear puntos para la función
            x_dense = np.linspace(a, b, 1000)
            y_dense = equation_data['numpy_function'](x_dense)

            fig = go.Figure()

            # Graficar función
            fig.add_trace(go.Scatter(
                x=x_dense, y=y_dense,
                mode='lines',
                name='f(x)',
                line=dict(color=self.colors[0], width=2),
                fill='tozeroy' if integration_data.get('fill', True) else None
            ))

            # Graficar puntos de evaluación
            if integration_data.get('points'):
                points_x, points_y = zip(*integration_data['points'])
                fig.add_trace(go.Scatter(
                    x=points_x, y=points_y,
                    mode='markers',
                    name='Puntos de evaluación',
                    marker=dict(color='red', size=6)
                ))

            # Graficar aproximación por trapecios/simpson si está disponible
            method = integration_data.get('method', '')
            if 'Trapecio' in method and integration_data.get('points'):
                points_x, points_y = zip(*integration_data['points'])

                # Agregar líneas para trapecios
                for i in range(len(points_x) - 1):
                    fig.add_trace(go.Scatter(
                        x=[points_x[i], points_x[i], points_x[i + 1], points_x[i + 1], points_x[i]],
                        y=[0, points_y[i], points_y[i + 1], 0, 0],
                        mode='lines',
                        name=f'Trapecio {i + 1}' if i == 0 else "",
                        line=dict(color='green', width=2),
                        fill='toself',
                        fillcolor='rgba(0,255,0,0.2)',
                        showlegend=(i == 0)
                    ))

            fig.update_layout(
                title=f"Integral Numérica - {method}",
                xaxis_title="x",
                yaxis_title="f(x)"
            )

            return fig

        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Error al generar gráfica: {str(e)}",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False)
            return fig

    def plot_edo_solution(self, solution_data):
        """Gráfica interactiva para soluciones de EDOs"""
        try:
            t = solution_data['t']
            y = solution_data['y']

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=t, y=y,
                mode='lines+markers',
                name='Solución numérica',
                line=dict(color=self.colors[0], width=2),
                marker=dict(size=4)
            ))

            fig.update_layout(
                title=f"Solución de EDO - {solution_data['method']}",
                xaxis_title="t",
                yaxis_title="y(t)"
            )

            return fig

        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Error al generar gráfica: {str(e)}",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False)
            return fig

    def plot_convergence(self, iterations_data, method_name):
        """Gráfica de convergencia para métodos iterativos"""
        try:
            iterations = list(range(1, len(iterations_data) + 1))
            errors = [iter['error'] for iter in iterations_data]

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=iterations, y=errors,
                mode='lines+markers',
                name='Error',
                line=dict(color=self.colors[1], width=2)
            ))

            fig.update_layout(
                title=f"Convergencia - {method_name}",
                xaxis_title="Iteración",
                yaxis_title="Error",
                yaxis_type="log"  # Escala logarítmica para mejor visualización
            )

            return fig

        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Error al generar gráfica: {str(e)}",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False)
            return fig