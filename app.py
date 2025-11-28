from shiny import App, ui, render, reactive
import numpy as np
import sympy as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from shinywidgets import output_widget, render_plotly

# Importar módulos de métodos numéricos
from modules.equation_parser import EquationParser
from modules.validation import InputValidator
from modules.plotting import InteractivePlotter

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

app_ui = ui.page_fluid(
    # HEAD: enlazar CSS y JS desde www/css y www/js
    ui.tags.head(
        # CSS
        ui.tags.link(rel="stylesheet", href="css/main.css"),
        ui.tags.link(rel="stylesheet", href="css/components.css"),
        ui.tags.link(rel="stylesheet", href="css/themes.css"),
        # JS
        ui.tags.script(src="js/equation-editor.js"),
        ui.tags.script(src="js/keyboard.js"),
        ui.tags.script(src="js/validation.js"),
    ),

    # Contenido envuelto en un div con tema
    ui.div(
        # Header
        ui.div(
            ui.div(
                ui.img(
                    src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png",
                    height="30px",
                    class_="me-2"
                ),
                "Calculadora de Métodos Numéricos",
                style=(
                    "display: flex; align-items: center; "
                    "font-size: 1.5rem; font-weight: bold;"
                )
            ),
            class_="main-header"
        ),

        # Layout principal
        ui.layout_sidebar(
            # Sidebar
            ui.sidebar(
                ui.div(
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
                    ui.input_action_button(
                        "calculate",
                        "Calcular",
                        class_="btn-primary w-100 mt-3"
                    ),

                    # Información del método
                    ui.output_ui("method_info"),
                ),
                width=350
            ),

            # Contenido principal
            ui.navset_tab(
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
                        # Gráfica (plotly)
                        ui.card(
                            ui.card_header("📈 Gráfica"),
                            output_widget("interactive_plot"),
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
                )
            )
        ),

        # Footer
        ui.div(
            "Calculadora de Métodos Numéricos - Desarrollado con Shiny for Python",
            class_="text-center p-3 text-muted"
        ),

        # 👈 Tema aplicado (puedes cambiar a theme-blue, theme-green, etc.)
        class_="theme-light"
    )
)


def server(input, output, session):
    # Estado reactivo
    calculation_result = reactive.Value(None)
    current_method = reactive.Value("")

    @reactive.Effect
    def update_methods():
        category = input.category_select()
        if category in METHODS:
            method_choices = {
                method_id: f"{data['icon']} {data['name']}"
                for method_id, data in METHODS[category]["methods"].items()
            }
            ui.update_select("method_select", choices=method_choices)

    @output
    @render.ui
    def input_panel():
        method_id = input.method_select()
        if not method_id:
            return ui.p("Seleccione un método para comenzar.", class_="text-muted")

        current_method.set(method_id)

        equation_input = ui.div(
            ui.div(
                ui.input_text(
                    "equation_input",
                    "Función f(x):",
                    placeholder="Ej: x**2 - 4, sin(x)*exp(x), etc."
                ),
                ui.output_ui("equation_validation"),
                class_="mb-3"
            ),
            math_keyboard(),
            class_="equation-editor-container"
        )

        specific_inputs = generate_specific_inputs(method_id)
        return ui.div(equation_input, specific_inputs)

    @output
    @render.ui
    def equation_validation():
        equation = input.equation_input()
        if not equation:
            return ui.div()

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
                ui.input_select(
                    "n_points",
                    "Número de puntos:",
                    choices={
                        "2": "2 puntos",
                        "3": "3 puntos",
                        "4": "4 puntos",
                        "5": "5 puntos"
                    }
                )
            ])

        elif method_id in ["euler", "euler_modified", "runge_kutta"]:
            inputs.extend([
                ui.input_numeric("y0_value", "Valor inicial y₀:", value=1.0),
                ui.input_numeric("t0_value", "t inicial:", value=0.0),
                ui.input_numeric("tf_value", "t final:", value=1.0),
                ui.input_numeric("step_size", "Tamaño de paso h:", value=0.1, step=0.01),
                ui.input_select(
                    "rk_order",
                    "Orden de Runge-Kutta:",
                    choices={"2": "2do orden", "4": "4to orden"}
                ) if method_id == "runge_kutta" else None
            ])

        elif method_id == "taylor":
            inputs.extend([
                ui.input_text("variable", "Variable:", value="x"),
                ui.input_numeric("expansion_point", "Punto de expansión:", value=0.0),
                ui.input_numeric("degree", "Grado del polinomio:", value=3, min=0),
                ui.input_numeric(
                    "approximation_point",
                    "Punto para aproximación (opcional):",
                    value=None,
                    step=0.1
                )
            ])

        elif method_id in ["jacobi", "gauss_seidel"]:
            inputs.extend([
                ui.input_text_area(
                    "matrix_input",
                    "Matriz A (una fila por línea):",
                    placeholder="2 1\n1 2",
                    rows=4
                ),
                ui.input_text(
                    "vector_input",
                    "Vector b (elementos separados por espacios):",
                    placeholder="3 3"
                ),
                ui.input_text(
                    "initial_guess_input",
                    "Vector inicial (opcional):",
                    placeholder="0 0"
                ),
                ui.input_numeric("tolerance", "Tolerancia:", value=1e-6, step=1e-8),
                ui.input_numeric("max_iterations", "Máximo de iteraciones:", value=100, min=1)
            ])

        elif method_id in ["gaussian_elimination", "gauss_jordan"]:
            inputs.extend([
                ui.input_text_area(
                    "matrix_input",
                    "Matriz A (una fila por línea):",
                    placeholder="2 1\n1 2",
                    rows=4
                ),
                ui.input_text(
                    "vector_input",
                    "Vector b (elementos separados por espacios):",
                    placeholder="3 3"
                ),
                ui.input_select(
                    "pivot_type",
                    "Tipo de pivoteo:",
                    choices={"partial": "Parcial", "total": "Total"}
                )
            ])

        inputs = [inp for inp in inputs if inp is not None]
        return ui.div(*inputs, class_="method-inputs")

    def get_required_variables(method_id):
        if method_id in ["euler", "euler_modified", "runge_kutta"]:
            return ['t', 'y']
        elif method_id == "taylor":
            try:
                var = input.variable()
                return [var] if var else ['x']
            except Exception:
                return ['x']
        else:
            return ['x']

    def math_keyboard():
        # Helper para crear cada tecla
        def key(label, value=None, key_type=None):
            classes = ["math-key"]
            if key_type:
                classes.append(key_type)

            return ui.tags.button(
                label,
                type="button",
                class_=" ".join(classes),  # 👈 AQUÍ se pone la clase CSS
                **{"data-value": value or label}  # 👈 valor que usará JS
            )

        return ui.div(
            ui.h6("Teclado matemático", class_="mb-3"),

            ui.div(
                key("7"), key("8"), key("9"), key("/", key_type="operator"),
                class_="keyboard-row"
            ),
            ui.div(
                key("4"), key("5"), key("6"), key("*", key_type="operator"),
                class_="keyboard-row"
            ),
            ui.div(
                key("1"), key("2"), key("3"), key("-", key_type="operator"),
                class_="keyboard-row"
            ),
            ui.div(
                key("0"), key("."), key("+", key_type="operator"),
                key("(", key_type="operator"), key(")", key_type="operator"),
                class_="keyboard-row"
            ),
            ui.div(
                key("sin", "sin(", "function"),
                key("cos", "cos(", "function"),
                key("tan", "tan(", "function"),
                key("exp", "exp(", "function"),
                key("ln", "ln(", "function"),
                class_="keyboard-row"
            ),

            # Fila de constantes y raíz/potencia
            ui.div(
                key("π", "π", "constant"),  # símbolo pi
                key("e", "e", "constant"),  # Euler
                key("^", "^", "operator"),  # potencia visual con ^
                key("√", "√(", "function"),  # símbolo de raíz y abre paréntesis
                class_="keyboard-row"
            ),

            class_="math-keyboard"
        )

    @output
    @render.ui
    def method_info():
        method_id = input.method_select()
        if not method_id:
            return ui.div()

        for category in METHODS.values():
            if method_id in category["methods"]:
                method_data = category["methods"][method_id]
                return ui.div(
                    ui.h5(f"{method_data['icon']} {method_data['name']}"),
                    ui.p(get_method_description(method_id), class_="text-muted small"),
                    class_="method-info"
                )
        return ui.div()

    @output
    @render.ui
    def results_panel():
        result = calculation_result()
        if not result:
            return ui.div(
                ui.h4("Resultados"),
                ui.p(
                    "Ejecute un cálculo para ver los resultados aquí.",
                    class_="text-muted"
                ),
                class_="results-placeholder"
            )

        if not result.get('success', False):
            return ui.div(
                ui.h4("❌ Error en el Cálculo"),
                ui.pre(result.get('error', 'Error desconocido'), class_="text-danger"),
                class_="alert alert-danger"
            )

        try:
            output_elements = [ui.h4("✅ Resultados Obtenidos")]

            if 'root' in result:
                output_elements.append(
                    ui.p(f"Raíz encontrada: {result['root']:.8f}")
                )

            if 'integral' in result:
                output_elements.append(
                    ui.p(f"Valor de la integral: {result['integral']:.8f}")
                )

            if 'solution' in result:
                if isinstance(result['solution'], (list, np.ndarray)):
                    sol_str = ", ".join([f"{x:.8f}" for x in result['solution']])
                    output_elements.append(ui.p(f"Solución: [{sol_str}]"))
                else:
                    output_elements.append(
                        ui.p(f"Solución: {result['solution']:.8f}")
                    )

            if 'iterations' in result and len(result['iterations']) > 0:
                output_elements.append(
                    ui.p(f"Número de iteraciones: {len(result['iterations'])}")
                )

            if 'final_error' in result:
                output_elements.append(
                    ui.p(f"Error final: {result['final_error']:.2e}")
                )

            if 'message' in result:
                output_elements.append(ui.p(result['message']))

            return ui.div(*output_elements, class_="results-success")

        except Exception as e:
            return ui.div(
                ui.h4("❌ Error al formatear resultados"),
                ui.pre(str(e), class_="text-danger"),
                class_="alert alert-danger"
            )

    @output
    @render_plotly
    def interactive_plot():
        result = calculation_result()
        method_id = input.method_select()

        if not result or not result.get('success', False):
            return create_empty_plot("Ejecute un cálculo para ver la gráfica")

        try:
            equation = input.equation_input()
            if not equation:
                return create_empty_plot("No hay ecuación para graficar")

            variables = get_required_variables(method_id)
            eq_data = equation_parser.parse_equation(equation, variables)

            if method_id in [
                "bisection", "false_position",
                "newton_raphson", "secant", "multiple_roots"
            ]:
                x_range = (-10, 10)
                try:
                    a = input.a_value()
                    b = input.b_value()
                    if a is not None and b is not None:
                        x_range = (min(a, b), max(a, b))
                except Exception:
                    pass

                return plotter.plot_root_finding(
                    equation_data=eq_data,
                    root_data=result,
                    x_range=x_range
                )

            elif method_id in [
                "trapezoidal", "simpson_13",
                "simpson_38", "gaussian_quadrature"
            ]:
                a = input.a_value() if 'a_value' in input else 0
                b = input.b_value() if 'b_value' in input else 1
                return plotter.plot_integration(
                    equation_data=eq_data,
                    integration_data=result,
                    a=a,
                    b=b
                )

            elif method_id in ["euler", "euler_modified", "runge_kutta"]:
                return plotter.plot_edo_solution(result)

            else:
                return create_empty_plot("Gráfica no disponible para este método")

        except Exception as e:
            return create_empty_plot(f"Error al generar gráfica: {str(e)}")

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

    @output
    @render.ui
    def examples_panel():
        method_id = input.method_select()
        if not method_id:
            return ui.p("Seleccione un método para ver ejemplos.")

        examples = get_method_examples(method_id)

        example_cards = []
        for i, example in enumerate(examples):
            card = ui.card(
                ui.card_header(f"Ejemplo {i + 1}"),
                ui.markdown(example['description']),
                class_="example-card"
            )
            example_cards.append(card)

        return ui.layout_columns(*example_cards, col_widths=[6, 6])

    @reactive.Effect
    @reactive.event(input.calculate)
    def perform_calculation():
        method_id = input.method_select()
        equation = input.equation_input()

        if not method_id or not equation:
            ui.notification_show(
                "Seleccione un método e ingrese una ecuación.",
                type="warning"
            )
            return

        variables = get_required_variables(method_id)
        is_valid, message = validator.validate_equation(equation, variables)
        if not is_valid:
            ui.notification_show(
                f"Ecuación inválida: {message}",
                type="error"
            )
            return

        try:
            result = execute_method(method_id, equation)
            calculation_result.set(result)

            if result.get('success', False):
                ui.notification_show(
                    "Cálculo completado exitosamente!",
                    type="message"
                )
            else:
                ui.notification_show(
                    f"Error en el cálculo: "
                    f"{result.get('error', 'Error desconocido')}",
                    type="error"
                )

        except Exception as e:
            ui.notification_show(
                f"Error inesperado: {str(e)}",
                type="error"
            )
            calculation_result.set({
                'success': False,
                'error': str(e)
            })

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
                matrix = parse_matrix_input(input.matrix_input())
                vector = parse_vector_input(input.vector_input())
                initial_guess = (
                    parse_vector_input(input.initial_guess_input())
                    if input.initial_guess_input() else None
                )

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
    if not matrix_str or matrix_str.strip() == "":
        raise ValueError("La matriz no puede estar vacía")

    rows = matrix_str.strip().split('\n')
    matrix = []
    for row in rows:
        elements = [float(x) for x in row.strip().split()]
        matrix.append(elements)
    return matrix

def parse_vector_input(vector_str):
    if not vector_str or vector_str.strip() == "":
        raise ValueError("El vector no puede estar vacía")

    return [float(x) for x in vector_str.strip().split()]

def get_method_name(method_id):
    for category in METHODS.values():
        if method_id in category["methods"]:
            return category["methods"][method_id]["name"]
    return "Método Desconocido"

def get_method_description(method_id, detailed=False):
    descriptions = {
        "bisection": "Método robusto que divide repetidamente el intervalo donde la función cambia de signo.",
        "false_position": "Variante mejorada de bisección que utiliza interpolación lineal para acelerar la convergencia.",
        "newton_raphson": "Método rápido que usa derivadas para aproximar la raíz. Requiere un buen valor inicial.",
        "secant": "Método que aproxima la derivada usando diferencias finitas. No necesita f'(x).",
        "multiple_roots": "Versión modificada de Newton para funciones con raíces de multiplicidad mayor que 1.",
        "jacobi": "Método iterativo que actualiza todas las componentes simultáneamente. Converge con matrices diagonalmente dominantes.",
        "gauss_seidel": "Similar a Jacobi pero usa valores actualizados en cada iteración, por lo general converge más rápido.",
        "gaussian_elimination": "Método directo que transforma la matriz en una forma triangular para resolver el sistema.",
        "gauss_jordan": "Extiende la eliminación gaussiana hasta obtener la matriz identidad, útil para invertir matrices.",
        "trapezoidal": "Método simple que aproxima el área bajo la curva usando trapecios.",
        "simpson_13": "Método preciso que usa parábolas para aproximar la integral. Requiere número par de subintervalos.",
        "simpson_38": "Variante de Simpson que usa polinomios cúbicos. Útil cuando el número de subintervalos es múltiplo de 3.",
        "gaussian_quadrature": "Método muy preciso que evalúa la función en puntos óptimos (raíces de polinomios ortogonales).",
        "euler": "Método simple de un paso para resolver EDOs usando aproximaciones lineales.",
        "euler_modified": "También llamado método de Heun; mejora Euler usando promedio de pendientes.",
        "runge_kutta": "Familia de métodos de alta precisión. RK4 es uno de los métodos más usados para EDOs.",
        "taylor": "Aproxima funciones mediante un polinomio que coincide con sus derivadas en un punto."
    }

    simple_descs = {
        "bisection": "Encuentra raíces dividiendo intervalos sucesivamente.",
        "false_position": "Encuentra raíces usando interpolación lineal.",
        "newton_raphson": "Método rápido basado en derivadas.",
        "secant": "Encuentra raíces sin derivadas usando dos puntos.",
        "multiple_roots": "Versión de Newton para raíces múltiples.",
        "jacobi": "Resuelve sistemas lineales iterativamente.",
        "gauss_seidel": "Iterativo, usa valores actualizados en cada paso.",
        "gaussian_elimination": "Resuelve sistemas lineales directamente.",
        "gauss_jordan": "Extiende Gauss para obtener la solución directa.",
        "trapezoidal": "Aproxima integrales con trapecios.",
        "simpson_13": "Integra usando parábolas (Simpson 1/3).",
        "simpson_38": "Integra usando polinomios cúbicos.",
        "gaussian_quadrature": "Integración de alta precisión con puntos óptimos.",
        "euler": "Resuelve EDOs con aproximación lineal.",
        "euler_modified": "Mejora Euler usando pendiente promedio.",
        "runge_kutta": "Resuelve EDOs con alta precisión (RK).",
        "taylor": "Aproxima funciones con polinomios de Taylor."
    }

    if detailed:
        return descriptions.get(method_id, "Descripción detallada no disponible.")
    else:
        return simple_descs.get(method_id, "Método numérico.")

def get_method_formula(method_id):
    formulas = {

        "bisection": """
    Algoritmo del Método de Bisección:
    1. Elegir un intervalo [a, b] donde f(a) y f(b) tengan signos opuestos.
    2. Calcular el punto medio: c = (a + b) / 2.
    3. Si f(c) es cero o el intervalo es suficientemente pequeño, detener.
    4. Si f(a) y f(c) tienen signos opuestos, reemplazar b por c; de lo contrario, reemplazar a por c.
    5. Repetir el proceso.
    """,

        "false_position": """
    Método de Falsa Posición:
    1. Elegir un intervalo [a, b] donde f(a) y f(b) tengan signos opuestos.
    2. Calcular c usando interpolación lineal:
       c = b - f(b) * (a - b) / (f(a) - f(b))
    3. Si f(c) es suficientemente pequeño, detener.
    4. Igual que en bisección, ajustar a o b según el signo.
    """,

        "newton_raphson": """
    Método de Newton-Raphson:
    x_nuevo = x - f(x) / f'(x)
    Repetir hasta que la diferencia entre valores consecutivos sea pequeña.
    """,

        "secant": """
    Método de la Secante:
    x_nuevo = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    No requiere derivadas. Usa dos valores iniciales.
    """,

        "multiple_roots": """
    Método para Raíces Múltiples:
    x_nuevo = x - [ f(x) * f'(x) ] / [ (f'(x))^2 - f(x) * f''(x) ]
    Mejora Newton cuando la raíz tiene multiplicidad mayor que 1.
    """,

        "jacobi": """
    Método de Jacobi:
    Cada variable se actualiza usando los valores de la iteración anterior.
    x_i(nuevo) = (1 / a_ii) * ( b_i - suma(a_ij * x_j(anterior)) )
    """,

        "gauss_seidel": """
    Método de Gauss-Seidel:
    Similar a Jacobi pero usa valores nuevos tan pronto como se calculan.
    """,

        "gaussian_elimination": """
    Eliminación Gaussiana:
    Consiste en transformar el sistema en una forma triangular y luego resolver por sustitución hacia atrás.
    """,

        "gauss_jordan": """
    Método Gauss-Jordan:
    Transforma la matriz en la identidad, dejando la solución directamente.
    Permite obtener también la matriz inversa.
    """,

        "trapezoidal": """
    Regla del Trapecio:
    Aproxima la integral sumando áreas de trapecios.
    Integral aproximada = h/2 * [ f(x0) + 2*f(x1) + ... + f(xn) ]
    donde h = (b - a) / n
    """,

        "simpson_13": """
    Regla de Simpson 1/3:
    Aproxima la integral usando parábolas.
    Funciona cuando el número de intervalos es par.
    """,

        "simpson_38": """
    Regla de Simpson 3/8:
    Aproxima la integral usando polinomios cúbicos.
    Funciona cuando el número de intervalos es múltiplo de 3.
    """,

        "gaussian_quadrature": """
    Cuadratura de Gauss:
    Método de integración muy preciso que evalúa la función en puntos óptimos dentro del intervalo.
    """,

        "euler": """
    Método de Euler:
    y_nuevo = y + h * f(t, y)
    Es simple pero puede ser inestable si el paso es muy grande.
    """,

        "euler_modified": """
    Método de Euler Modificado (Heun):
    Promedia dos pendientes:
       k1 = f(t, y)
       k2 = f(t + h, y + h*k1)
    y_nuevo = y + h*(k1 + k2)/2
    """,

        "runge_kutta": """
    Runge-Kutta de cuarto orden (RK4):
    Calcula 4 pendientes y las combina:
    k1 = f(t, y)
    k2 = f(t + h/2, y + h*k1/2)
    k3 = f(t + h/2, y + h*k2/2)
    k4 = f(t + h, y + h*k3)
    y_nuevo = y + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
    """,

        "taylor": """
    Serie de Taylor:
    Aproxima una función usando un polinomio alrededor de un punto.
    P(x) = f(a) + f'(a)*(x - a) + f''(a)/2*(x - a)^2 + ...
    """
    }

    return formulas.get(method_id, None)

def get_method_examples(method_id):
    examples = {
        "bisection": [
            {
                "description":
                    "Ejemplo 1: Encontrar la raíz de la ecuación x^2 - 4 en el intervalo [1, 3]\n"
                    "- Ecuación: x^2 - 4\n"
                    "- Intervalo: a = 1, b = 3\n"
                    "- Tolerancia: 1e-6"
            },
            {
                "description":
                    "Ejemplo 2: Encontrar la raíz de la función sin(x) en el intervalo [3, 4]\n"
                    "- Ecuación: sin(x)\n"
                    "- Intervalo: a = 3, b = 4\n"
                    "- Tolerancia: 1e-8"
            }
        ],

        "false_position": [
            {
                "description":
                    "Ejemplo 1: Raíz de la función exp(-x) - x en el intervalo [0, 1]\n"
                    "- Ecuación: exp(-x) - x\n"
                    "- Intervalo: a = 0, b = 1\n"
                    "- Tolerancia: 1e-5"
            },
            {
                "description":
                    "Ejemplo 2: Raíz de la función x^3 - x - 1 en [1, 2]\n"
                    "- Ecuación: x^3 - x - 1\n"
                    "- Intervalo: a = 1, b = 2\n"
                    "- Tolerancia: 1e-6"
            }
        ],

        "newton_raphson": [
            {
                "description":
                    "Ejemplo 1: Raíz de la ecuación x^3 - 2x - 5 usando Newton-Raphson\n"
                    "- Ecuación: x^3 - 2*x - 5\n"
                    "- Valor inicial: 2.0\n"
                    "- Tolerancia: 1e-6"
            },
            {
                "description":
                    "Ejemplo 2: Raíz de cos(x) - x\n"
                    "- Ecuación: cos(x) - x\n"
                    "- Valor inicial: 1.0\n"
                    "- Tolerancia: 1e-7"
            }
        ],

        "secant": [
            {
                "description":
                    "Ejemplo 1: Raíz de x^3 - x - 1 usando método de la secante\n"
                    "- Ecuación: x^3 - x - 1\n"
                    "- x0 = 1.0, x1 = 2.0\n"
                    "- Tolerancia: 1e-6"
            },
            {
                "description":
                    "Ejemplo 2: Raíz de exp(x) - 3x\n"
                    "- Ecuación: exp(x) - 3*x\n"
                    "- x0 = 0, x1 = 1\n"
                    "- Tolerancia: 1e-6"
            }
        ],

        "multiple_roots": [
            {
                "description":
                    "Ejemplo 1: Raíz múltiple de (x - 2)^3\n"
                    "- Ecuación: (x - 2)^3\n"
                    "- Valor inicial: 3.0\n"
                    "- Tolerancia: 1e-6"
            },
            {
                "description":
                    "Ejemplo 2: Raíz múltiple de (x - 1)^2 * exp(x)\n"
                    "- Ecuación: (x - 1)^2 * exp(x)\n"
                    "- Valor inicial: 0.5\n"
                    "- Tolerancia: 1e-5"
            }
        ],
        "jacobi": [
            {
                "description":
                    "Ejemplo 1: Resolver el sistema Ax = b usando Jacobi\n"
                    "Matriz A:\n"
                    "4 1\n"
                    "2 3\n"
                    "Vector b: 1 2\n"
                    "Vector inicial: 0 0\n"
                    "Tolerancia: 1e-6"
            }
        ],

        "gauss_seidel": [
            {
                "description":
                    "Ejemplo 1: Resolver el sistema Ax = b usando Gauss-Seidel\n"
                    "Matriz A:\n"
                    "4 1\n"
                    "2 3\n"
                    "Vector b: 1 2\n"
                    "Vector inicial: 0 0\n"
                    "Tolerancia: 1e-6"
            }
        ],

        "gaussian_elimination": [
            {
                "description":
                    "Ejemplo 1: Resolver sistema lineal mediante eliminación gaussiana\n"
                    "Matriz A:\n"
                    "2 1 -1\n"
                    "-3 -1 2\n"
                    "-2 1 2\n"
                    "Vector b: 8 -11 -3"
            }
        ],

        "gauss_jordan": [
            {
                "description":
                    "Ejemplo 1: Resolver sistema lineal con Gauss-Jordan\n"
                    "Matriz A:\n"
                    "1 2 3\n"
                    "0 1 4\n"
                    "5 6 0\n"
                    "Vector b: 7 8 9"
            }
        ],

        "trapezoidal": [
            {
                "description":
                    "Ejemplo 1: Aproximar la integral de x^2 en [0, 2]\n"
                    "- Ecuación: x^2\n"
                    "- a = 0, b = 2\n"
                    "- n = 20"
            }
        ],

        "simpson_13": [
            {
                "description":
                    "Ejemplo 1: Aproximar la integral de sin(x) en [0, pi] usando Simpson 1/3\n"
                    "- Ecuación: sin(x)\n"
                    "- a = 0, b = pi\n"
                    "- n = 100"
            }
        ],

        "simpson_38": [
            {
                "description":
                    "Ejemplo 1: Aproximar la integral de exp(-x^2) en [0, 1] usando Simpson 3/8\n"
                    "- Ecuación: exp(-x^2)\n"
                    "- a = 0, b = 1\n"
                    "- n = 12"
            }
        ],

        "gaussian_quadrature": [
            {
                "description":
                    "Ejemplo 1: Aproximar la integral de x^3 en [0, 1] usando cuadratura de Gauss con 3 puntos\n"
                    "- Ecuación: x^3\n"
                    "- a = 0, b = 1\n"
                    "- Puntos: 3"
            }
        ],

        "euler": [
            {
                "description":
                    "Ejemplo 1: Resolver la EDO y' = y - t^2 + 1\n"
                    "- Ecuación: y - t^2 + 1\n"
                    "- y0 = 0.5\n"
                    "- t0 = 0, tf = 2\n"
                    "- h = 0.2"
            }
        ],

        "euler_modified": [
            {
                "description":
                    "Ejemplo 1: Resolver la EDO y' = t + y usando Euler modificado\n"
                    "- Ecuación: t + y\n"
                    "- y0 = 1\n"
                    "- t0 = 0, tf = 1\n"
                    "- h = 0.1"
            }
        ],

        "runge_kutta": [
            {
                "description":
                    "Ejemplo 1: Resolver la EDO y' = y*cos(t) usando RK4\n"
                    "- Ecuación: y*cos(t)\n"
                    "- y0 = 1\n"
                    "- t0 = 0, tf = 3\n"
                    "- h = 0.1"
            }
        ],

        "taylor": [
            {
                "description":
                    "Ejemplo 1: Polinomio de Taylor de exp(x) alrededor de x = 0\n"
                    "- Ecuación: exp(x)\n"
                    "- Grado: 4\n"
                    "- Punto de expansión: 0"
            },
            {
                "description":
                    "Ejemplo 2: Polinomio de Taylor de sin(x) alrededor de pi/2\n"
                    "- Ecuación: sin(x)\n"
                    "- Grado: 3\n"
                    "- Punto de expansión: pi/2"
            }
        ]
    }

    return examples.get(method_id, [])


app_dir = Path(__file__).parent
app = App(app_ui, server, static_assets=app_dir / "www")