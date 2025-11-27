from shiny import App, ui, render, reactive
import numpy as np
import sympy as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importar módulos de métodos numéricos
from modules.equation_parser import EquationParser
from modules.validation import InputValidator
from modules.plotting import InteractivePlotter
from utils.formatters import ResultFormatter
from utils.math_functions import MathUtils

# Métodos de búsqueda de raíces
from modules.root_finding.bisection import BisectionMethod
from modules.root_finding.false_position import FalsePositionMethod
from modules.root_finding.newton_raphson import NewtonRaphsonMethod
from modules.root_finding.secant import SecantMethod
from modules.root_finding.multiple_roots import MultipleRootsMethod

# Sistemas lineales
from modules.linear_systems.jacobi import JacobiMethod
from modules.linear_systems.gauss_seidel import GaussSeidelMethod
from modules.linear_systems.gaussian_elimination import GaussianElimination, GaussJordanElimination

# Integración numérica
from modules.integration.simpson import SimpsonIntegration
from modules.integration.trapecio import TrapezoidalRule
from modules.integration.gaussian_quadrature import GaussianQuadrature

# EDOs
from modules.edo.euler import EulerMethod
from modules.edo.euler_modified import ModifiedEulerMethod
from modules.edo.runge_kutta import RungeKuttaMethod

# Taylor
from modules.taylor import TaylorPolynomial

# Inicializar componentes globales
equation_parser = EquationParser()
validator = InputValidator()
plotter = InteractivePlotter()
formatter = ResultFormatter()

# Definir métodos disponibles
METHODS = {
    "raices": {
        "name": "Búsqueda de Raíces",
        "methods": {
            "bisection": {"name": "Método de Bisección", "icon": "🔍"},
            "false_position": {"name": "Falsa Posición", "icon": "📐"},
            "newton_raphson": {"name": "Newton-Raphson", "icon": "📈"},
            "secant": {"name": "Método de la Secante", "icon": "📊"},
            "multiple_roots": {"name": "Raíces Múltiples", "icon": "🔢"}
        }
    },
    "lineales": {
        "name": "Sistemas Lineales",
        "methods": {
            "jacobi": {"name": "Método de Jacobi", "icon": "🔄"},
            "gauss_seidel": {"name": "Gauss-Seidel", "icon": "⚡"},
            "gaussian_elimination": {"name": "Eliminación Gaussiana", "icon": "🎯"},
            "gauss_jordan": {"name": "Gauss-Jordan", "icon": "🔍"}
        }
    },
    "integracion": {
        "name": "Integración Numérica",
        "methods": {
            "trapezoidal": {"name": "Regla del Trapecio", "icon": "📏"},
            "simpson_13": {"name": "Simpson 1/3", "icon": "📐"},
            "simpson_38": {"name": "Simpson 3/8", "icon": "📊"},
            "gaussian_quadrature": {"name": "Cuadratura de Gauss", "icon": "🎯"}
        }
    },
    "edos": {
        "name": "Ecuaciones Diferenciales",
        "methods": {
            "euler": {"name": "Método de Euler", "icon": "📈"},
            "euler_modified": {"name": "Euler Modificado", "icon": "⚡"},
            "runge_kutta": {"name": "Runge-Kutta", "icon": "🎯"}
        }
    },
    "taylor": {
        "name": "Series de Taylor",
        "methods": {
            "taylor": {"name": "Polinomios de Taylor", "icon": "📚"}
        }
    }
}

# Definición de la UI
app_ui = ui.page_navbar(
    # Título (primer argumento posicional)
    ui.div(
        ui.img(src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png", height="30px", class_="me-2"),
        "Calculadora de Métodos Numéricos",
        style="display: flex; align-items: center;"
    ),

    # Pestañas principales (argumentos posicionales)
    ui.nav_panel(
        "Calculadora",
        ui.layout_columns(
            # Resultados
            ui.card(
                ui.card_header("📊 Resultados"),
                ui.output_ui("results_panel"),
                height="500px",
                class_="overflow-auto"
            ),
            # Gráfica
            ui.card(
                ui.card_header("📈 Gráfica"),
                ui.output_plot("interactive_plot"),
                height="500px"
            ),
            col_widths=[6, 6]
        )
    ),

    ui.nav_panel(
        "Información",
        ui.card(
            ui.card_header("ℹ️ Información del Método"),
            ui.output_ui("method_details")
        )
    ),

    ui.nav_panel(
        "Ejemplos",
        ui.card(
            ui.card_header("💡 Ejemplos Predefinidos"),
            ui.output_ui("examples_panel")
        )
    ),

    # CSS y JS (argumentos posicionales)
    ui.include_css("static/css/main.css"),
    ui.include_css("static/css/components.css"),
    ui.include_js("static/js/equation-editor.js"),
    ui.include_js("static/js/validation.js"),
    ui.include_js("static/js/keyboard.js"),

    # Argumentos con nombre (deben ir al final)
    sidebar=ui.sidebar(
        # Selector de categoría
        ui.input_select(
            "category_select",
            "Seleccionar Categoría:",
            choices={cat: data["name"] for cat, data in METHODS.items()}
        ),

        # Selector de método específico
        ui.input_select(
            "method_select",
            "Seleccionar Método:",
            choices={}
        ),

        # Panel de entrada dinámico
        ui.output_ui("input_panel"),

        # Botón de cálculo
        ui.input_action_button("calculate", "Calcular", class_="btn-primary w-100 mt-3"),

        # Información del método
        ui.output_ui("method_info"),

        width=350,
        class_="p-3"
    ),

    footer=ui.div(
        "Calculadora de Métodos Numéricos - Desarrollado con Shiny for Python",
        class_="text-center p-3 text-muted"
    ),

    bg="#0066cc",
    inverse=True,

    # Estilos adicionales - Corregido
    theme="flatly"
)


def server(input, output, session):
    # Estado reactivo
    calculation_result = reactive.Value(None)
    current_method = reactive.Value("")

    # Actualizar métodos cuando cambia la categoría
    @reactive.Effect
    def update_methods():
        category = input.category_select()
        if category in METHODS:
            method_choices = {
                method_id: f"{data['icon']} {data['name']}"
                for method_id, data in METHODS[category]["methods"].items()
            }
            ui.update_select("method_select", choices=method_choices)

    # Generar panel de entrada dinámico
    @output
    @render.ui
    def input_panel():
        method_id = input.method_select()
        if not method_id:
            return ui.p("Seleccione un método para comenzar.", class_="text-muted")

        current_method.set(method_id)

        # Panel común para ecuaciones
        equation_input = ui.div(
            ui.input_text(
                "equation_input",
                "Función f(x):",
                placeholder="Ej: x**2 - 4, sin(x)*exp(x), etc.",
                class_="equation-input"
            ),
            ui.output_ui("equation_validation"),
            class_="mb-3"
        )

        # Inputs específicos por método
        specific_inputs = generate_specific_inputs(method_id)

        return ui.div(equation_input, specific_inputs)

    # Validación de ecuación en tiempo real
    @output
    @render.ui
    def equation_validation():
        equation = input.equation_input()
        if not equation:
            return ui.div()

        # Determinar variables requeridas
        variables = get_required_variables(input.method_select())

        is_valid, message = validator.validate_equation(equation, variables)

        if is_valid:
            return ui.div(
                ui.span("✓ ", class_="text-success"),
                ui.span(message, class_="text-success"),
                class_="small"
            )
        else:
            return ui.div(
                ui.span("✗ ", class_="text-danger"),
                ui.span(message, class_="text-danger"),
                class_="small"
            )

    # Generar inputs específicos para cada método
    def generate_specific_inputs(method_id):
        inputs = []

        if method_id in ["bisection", "false_position"]:
            inputs.extend([
                ui.input_numeric("a_value", "Límite inferior a:", value=-2.0),
                ui.input_numeric("b_value", "Límite superior b:", value=2.0),
                ui.input_numeric("tolerance", "Tolerancia:", value=1e-6, step=1e-8),
                ui.input_numeric("max_iterations", "Máximo de iteraciones:", value=100, min=1)
            ])

        elif method_id in ["newton_raphson", "multiple_roots"]:
            inputs.extend([
                ui.input_numeric("initial_guess", "Valor inicial x₀:", value=1.0),
                ui.input_numeric("tolerance", "Tolerancia:", value=1e-6, step=1e-8),
                ui.input_numeric("max_iterations", "Máximo de iteraciones:", value=100, min=1)
            ])

        elif method_id == "secant":
            inputs.extend([
                ui.input_numeric("x0_value", "x₀:", value=0.0),
                ui.input_numeric("x1_value", "x₁:", value=1.0),
                ui.input_numeric("tolerance", "Tolerancia:", value=1e-6, step=1e-8),
                ui.input_numeric("max_iterations", "Máximo de iteraciones:", value=100, min=1)
            ])

        elif method_id in ["trapezoidal", "simpson_13", "simpson_38"]:
            inputs.extend([
                ui.input_numeric("a_value", "Límite inferior a:", value=0.0),
                ui.input_numeric("b_value", "Límite superior b:", value=1.0),
                ui.input_numeric("n_intervals", "Número de intervalos:", value=10, min=1)
            ])

        elif method_id == "gaussian_quadrature":
            inputs.extend([
                ui.input_numeric("a_value", "Límite inferior a:", value=0.0),
                ui.input_numeric("b_value", "Límite superior b:", value=1.0),
                ui.input_select("n_points", "Número de puntos:",
                                choices={"2": "2 puntos", "3": "3 puntos",
                                         "4": "4 puntos", "5": "5 puntos"})
            ])

        elif method_id in ["euler", "euler_modified", "runge_kutta"]:
            inputs.extend([
                ui.input_numeric("y0_value", "Valor inicial y₀:", value=1.0),
                ui.input_numeric("t0_value", "t inicial:", value=0.0),
                ui.input_numeric("tf_value", "t final:", value=1.0),
                ui.input_numeric("step_size", "Tamaño de paso h:", value=0.1, step=0.01),
                ui.input_select("rk_order", "Orden de Runge-Kutta:",
                                choices={"2": "2do orden", "4": "4to orden"})
                if method_id == "runge_kutta" else None
            ])

        elif method_id == "taylor":
            inputs.extend([
                ui.input_text("variable", "Variable:", value="x"),
                ui.input_numeric("expansion_point", "Punto de expansión:", value=0.0),
                ui.input_numeric("degree", "Grado del polinomio:", value=3, min=0),
                ui.input_numeric("approximation_point", "Punto para aproximación (opcional):",
                                 value=None, step=0.1)
            ])

        elif method_id in ["jacobi", "gauss_seidel"]:
            inputs.extend([
                ui.input_text_area("matrix_input", "Matriz A (una fila por línea):",
                                   placeholder="2 1\n1 2", rows=4),
                ui.input_text("vector_input", "Vector b (elementos separados por espacios):",
                              placeholder="3 3"),
                ui.input_text("initial_guess_input", "Vector inicial (opcional):",
                              placeholder="0 0"),
                ui.input_numeric("tolerance", "Tolerancia:", value=1e-6, step=1e-8),
                ui.input_numeric("max_iterations", "Máximo de iteraciones:", value=100, min=1)
            ])

        elif method_id in ["gaussian_elimination", "gauss_jordan"]:
            inputs.extend([
                ui.input_text_area("matrix_input", "Matriz A (una fila por línea):",
                                   placeholder="2 1\n1 2", rows=4),
                ui.input_text("vector_input", "Vector b (elementos separados por espacios):",
                              placeholder="3 3"),
                ui.input_select("pivot_type", "Tipo de pivoteo:",
                                choices={"partial": "Parcial", "total": "Total"})
            ])

        # Filtrar elementos None
        inputs = [inp for inp in inputs if inp is not None]

        return ui.div(*inputs, class_="method-inputs")

    # Obtener variables requeridas para cada método
    def get_required_variables(method_id):
        if method_id in ["euler", "euler_modified", "runge_kutta"]:
            return ['t', 'y']
        elif method_id == "taylor":
            return [getattr(input, "variable", lambda: "x")() or "x"]
        else:
            return ['x']

    # Información del método seleccionado
    @output
    @render.ui
    def method_info():
        method_id = input.method_select()
        if not method_id:
            return ui.div()

        # Buscar información del método
        for category in METHODS.values():
            if method_id in category["methods"]:
                method_data = category["methods"][method_id]
                return ui.div(
                    ui.h5(f"{method_data['icon']} {method_data['name']}"),
                    ui.p(get_method_description(method_id), class_="text-muted small"),
                    class_="method-info"
                )

        return ui.div()

    # Panel de resultados
    @output
    @render.ui
    def results_panel():
        result = calculation_result()
        if not result:
            return ui.div(
                ui.h4("Resultados"),
                ui.p("Ejecute un cálculo para ver los resultados aquí.", class_="text-muted"),
                class_="results-placeholder"
            )

        if not result.get('success', False):
            return ui.div(
                ui.h4("❌ Error en el Cálculo"),
                ui.pre(result.get('error', 'Error desconocido'), class_="text-danger"),
                class_="alert alert-danger"
            )

        formatted = formatter.format_method_result(result,
                                                   METHODS.get(input.category_select(), {})
                                                   .get('methods', {})
                                                   .get(input.method_select(), {})
                                                   .get('name', 'Método'))

        if formatted['success']:
            return ui.div(
                ui.h4("✅ Resultados Obtenidos"),
                ui.markdown(formatted['formatted_output']),
                class_="results-success"
            )
        else:
            return ui.div(
                ui.h4("❌ Error"),
                ui.markdown(formatted['formatted_output']),
                class_="alert alert-danger"
            )

    # Gráfica interactiva
    @output
    @render.plot
    def interactive_plot():
        result = calculation_result()
        method_id = input.method_select()

        if not result or not result.get('success', False):
            # Gráfica por defecto
            fig = go.Figure()
            fig.add_annotation(
                text="Ejecute un cálculo para ver la gráfica",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
            return fig

        # Generar gráfica según el método
        try:
            equation = input.equation_input()
            if not equation:
                return create_empty_plot("No hay ecuación para graficar")

            if method_id in ["bisection", "false_position", "newton_raphson", "secant", "multiple_roots"]:
                # Gráfica para métodos de raíces
                return plotter.plot_root_finding(
                    equation_data=result.get('plot_data', {}),
                    root_data=result,
                    method_name=METHODS.get(input.category_select(), {})
                    .get('methods', {})
                    .get(method_id, {})
                    .get('name', '')
                )

            elif method_id in ["trapezoidal", "simpson_13", "simpson_38", "gaussian_quadrature"]:
                # Gráfica para integración
                return plotter.plot_integration(
                    equation_data=result.get('plot_data', {}),
                    integration_data=result
                )

            elif method_id in ["euler", "euler_modified", "runge_kutta"]:
                # Gráfica para EDOs
                return plotter.plot_ode_solution(result)

            elif method_id == "taylor":
                # Gráfica para Taylor
                return plotter.plot_taylor_approximation(result)

            else:
                return create_empty_plot("Gráfica no disponible para este método")

        except Exception as e:
            return create_empty_plot(f"Error al generar gráfica: {str(e)}")

    # Detalles del método
    @output
    @render.ui
    def method_details():
        method_id = input.method_select()
        if not method_id:
            return ui.p("Seleccione un método para ver sus detalles.")

        description = get_method_description(method_id, detailed=True)
        formula = get_method_formula(method_id)

        return ui.div(
            ui.h4(f"📖 {get_method_name(method_id)}"),
            ui.markdown(description),
            ui.hr(),
            ui.h5("🧮 Fórmula:"),
            ui.markdown(formula) if formula else ui.p("Fórmula no disponible."),
            class_="method-details"
        )

    # Panel de ejemplos
    @output
    @render.ui
    def examples_panel():
        method_id = input.method_select()
        if not method_id:
            return ui.p("Seleccione un método para ver ejemplos.")

        examples = get_method_examples(method_id)

        example_cards = []
        for i, example in enumerate(examples):
            example_cards.append(
                ui.card(
                    ui.card_header(f"Ejemplo {i + 1}"),
                    ui.markdown(example['description']),
                    ui.input_action_button(f"load_example_{i}", "Cargar Ejemplo",
                                           class_="btn-outline-primary btn-sm"),
                    class_="example-card"
                )
            )

        return ui.layout_columns(*example_cards, col_widths=[6, 6])

    # Cálculo principal
    @reactive.Effect
    @reactive.event(input.calculate)
    def perform_calculation():
        method_id = input.method_select()
        equation = input.equation_input()

        if not method_id or not equation:
            ui.notification_show("Seleccione un método e ingrese una ecuación.", type="warning")
            return

        # Validar ecuación
        variables = get_required_variables(method_id)
        is_valid, message = validator.validate_equation(equation, variables)
        if not is_valid:
            ui.notification_show(f"Ecuación inválida: {message}", type="error")
            return

        try:
            # Ejecutar método específico
            result = execute_method(method_id, equation)
            calculation_result.set(result)

            if result.get('success', False):
                ui.notification_show("Cálculo completado exitosamente!", type="message")
            else:
                ui.notification_show(f"Error en el cálculo: {result.get('error', 'Error desconocido')}",
                                     type="error")

        except Exception as e:
            ui.notification_show(f"Error inesperado: {str(e)}", type="error")
            calculation_result.set({
                'success': False,
                'error': str(e)
            })

    # Ejecutar método específico
    def execute_method(method_id, equation):
        try:
            if method_id == "bisection":
                return BisectionMethod().solve(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    input.tolerance(),
                    input.max_iterations()
                )

            elif method_id == "false_position":
                return FalsePositionMethod().solve(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    input.tolerance(),
                    input.max_iterations()
                )

            elif method_id == "newton_raphson":
                return NewtonRaphsonMethod().solve(
                    equation,
                    input.initial_guess(),
                    input.tolerance(),
                    input.max_iterations()
                )

            elif method_id == "secant":
                return SecantMethod().solve(
                    equation,
                    input.x0_value(),
                    input.x1_value(),
                    input.tolerance(),
                    input.max_iterations()
                )

            elif method_id == "multiple_roots":
                return MultipleRootsMethod().solve(
                    equation,
                    input.initial_guess(),
                    input.tolerance(),
                    input.max_iterations()
                )

            elif method_id == "trapezoidal":
                return TrapezoidalRule().solve(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    input.n_intervals()
                )

            elif method_id == "simpson_13":
                return SimpsonIntegration().simpson_13(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    input.n_intervals()
                )

            elif method_id == "simpson_38":
                return SimpsonIntegration().simpson_38(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    input.n_intervals()
                )

            elif method_id == "gaussian_quadrature":
                return GaussianQuadrature().solve(
                    equation,
                    input.a_value(),
                    input.b_value(),
                    int(input.n_points())
                )

            elif method_id == "euler":
                return EulerMethod().solve(
                    equation,
                    input.y0_value(),
                    input.t0_value(),
                    input.tf_value(),
                    input.step_size()
                )

            elif method_id == "euler_modified":
                return ModifiedEulerMethod().solve(
                    equation,
                    input.y0_value(),
                    input.t0_value(),
                    input.tf_value(),
                    input.step_size()
                )

            elif method_id == "runge_kutta":
                return RungeKuttaMethod().solve(
                    equation,
                    input.y0_value(),
                    input.t0_value(),
                    input.tf_value(),
                    input.step_size(),
                    order=int(input.rk_order())
                )

            elif method_id == "taylor":
                taylor_result = TaylorPolynomial().expand(
                    equation,
                    input.variable(),
                    input.expansion_point(),
                    input.degree()
                )

                if input.approximation_point() is not None:
                    approx_result = TaylorPolynomial().approximate(
                        equation,
                        input.variable(),
                        input.expansion_point(),
                        input.degree(),
                        input.approximation_point()
                    )
                    taylor_result['approximation'] = approx_result

                return taylor_result

            elif method_id in ["jacobi", "gauss_seidel"]:
                # Parsear matriz y vector
                matrix = parse_matrix_input(input.matrix_input())
                vector = parse_vector_input(input.vector_input())
                initial_guess = parse_vector_input(input.initial_guess_input()) if input.initial_guess_input() else None

                if method_id == "jacobi":
                    return JacobiMethod().solve(
                        matrix, vector, initial_guess,
                        input.tolerance(), input.max_iterations()
                    )
                else:
                    return GaussSeidelMethod().solve(
                        matrix, vector, initial_guess,
                        input.tolerance(), input.max_iterations()
                    )

            elif method_id in ["gaussian_elimination", "gauss_jordan"]:
                matrix = parse_matrix_input(input.matrix_input())
                vector = parse_vector_input(input.vector_input())

                if method_id == "gaussian_elimination":
                    return GaussianElimination().solve(
                        matrix, vector, input.pivot_type()
                    )
                else:
                    return GaussJordanElimination().solve(
                        matrix, vector, input.pivot_type()
                    )

            else:
                return {
                    'success': False,
                    'error': f"Método '{method_id}' no implementado"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Funciones auxiliares
def create_empty_plot(message):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    return fig


def parse_matrix_input(matrix_str):
    rows = matrix_str.strip().split('\n')
    matrix = []
    for row in rows:
        elements = [float(x) for x in row.strip().split()]
        matrix.append(elements)
    return matrix


def parse_vector_input(vector_str):
    return [float(x) for x in vector_str.strip().split()]


def get_method_name(method_id):
    for category in METHODS.values():
        if method_id in category["methods"]:
            return category["methods"][method_id]["name"]
    return "Método Desconocido"


def get_method_description(method_id, detailed=False):
    descriptions = {
        "bisection": "El método de bisección es un algoritmo simple y robusto para encontrar raíces de funciones continuas. Divide repetidamente el intervalo a la mitad y selecciona el subintervalo donde la función cambia de signo.",
        "newton_raphson": "Método iterativo que usa derivadas para converger rápidamente a la raíz. Requiere una buena estimación inicial y que la derivada no sea cero.",
        "trapezoidal": "Aproxima la integral usando trapecios. Simple pero menos preciso que Simpson para funciones suaves.",
        # ... agregar más descripciones
    }

    simple_descs = {
        "bisection": "Encuentra raíces dividiendo intervalos sucesivamente.",
        "newton_raphson": "Método rápido que usa derivadas para encontrar raíces.",
        "trapezoidal": "Aproxima integrales usando la regla del trapecio.",
    }

    if detailed:
        return descriptions.get(method_id, "Descripción detallada no disponible.")
    else:
        return simple_descs.get(method_id, "Método numérico.")


def get_method_formula(method_id):
    formulas = {
        "bisection": r"""
        **Algoritmo:**
        1. Sea $[a,b]$ tal que $f(a) \cdot f(b) < 0$
        2. $c = \frac{a + b}{2}$
        3. Si $f(c) = 0$ o $|b-a| < \text{tol}$, terminar
        4. Si $f(a) \cdot f(c) < 0$, $b = c$, sino $a = c$
        5. Repetir desde 2
        """,
        "newton_raphson": r"""
        **Fórmula iterativa:**
        $$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$
        """,
        # ... agregar más fórmulas
    }
    return formulas.get(method_id, None)


def get_method_examples(method_id):
    examples = {
        "bisection": [
            {
                "description": "**Ejemplo 1:** Raíz de $x^2 - 4$ en $[1, 3]$\n- Ecuación: `x**2 - 4`\n- a = 1, b = 3\n- Tolerancia = 1e-6"
            },
            {
                "description": "**Ejemplo 2:** Raíz de $sin(x)$ en $[3, 4]$\n- Ecuación: `sin(x)`\n- a = 3, b = 4\n- Tolerancia = 1e-8"
            }
        ],
        # ... agregar más ejemplos
    }
    return examples.get(method_id, [])


app = App(app_ui, server)