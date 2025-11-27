class EquationValidator {
    constructor(inputElement, errorContainer, options = {}) {
        this.input = inputElement;
        this.errorContainer = errorContainer;
        this.options = Object.assign({
            allowedVariables: ['x', 'y', 't', 'z'],
            allowedFunctions: ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'exp', 'log', 'ln', 'sqrt', 'abs'],
            requireVariables: true
        }, options);

        this.setupValidation();
    }

    setupValidation() {
        // Validar en tiempo real mientras se escribe
        this.input.addEventListener('input', this.validate.bind(this));

        // Validar al perder el foco
        this.input.addEventListener('blur', this.validate.bind(this));

        // Validar al cargar la página si ya tiene valor
        if (this.input.value) {
            setTimeout(() => this.validate(), 100);
        }
    }

    validate() {
        const equation = this.input.value.trim();

        if (!equation) {
            this.showError('La ecuación no puede estar vacía');
            return false;
        }

        // Validaciones básicas
        const errors = [];

        // 1. Validar paréntesis balanceados
        if (!this.checkParentheses(equation)) {
            errors.push('Paréntesis no balanceados');
        }

        // 2. Validar caracteres permitidos
        const invalidChars = this.findInvalidCharacters(equation);
        if (invalidChars.length > 0) {
            errors.push(`Caracteres no permitidos: ${invalidChars.join(', ')}`);
        }

        // 3. Validar estructura de funciones
        const functionErrors = this.validateFunctions(equation);
        errors.push(...functionErrors);

        // 4. Validar variables
        if (this.options.requireVariables) {
            const variableErrors = this.validateVariables(equation);
            errors.push(...variableErrors);
        }

        // 5. Validar operadores consecutivos
        const operatorErrors = this.validateOperators(equation);
        errors.push(...operatorErrors);

        if (errors.length > 0) {
            this.showError(errors.join('. '));
            return false;
        } else {
            this.showSuccess('Ecuación válida');
            return true;
        }
    }

    checkParentheses(equation) {
        let balance = 0;
        for (let char of equation) {
            if (char === '(') balance++;
            if (char === ')') balance--;
            if (balance < 0) return false; // Más cierres que aperturas
        }
        return balance === 0;
    }

    findInvalidCharacters(equation) {
        const allowedChars = /^[0-9+\-*/().^ xyztsincaoghplqrtmbd\s]+$/i;
        const invalidChars = [];

        for (let char of equation) {
            if (!allowedChars.test(char) && !invalidChars.includes(char)) {
                invalidChars.push(char);
            }
        }

        return invalidChars;
    }

    validateFunctions(equation) {
        const errors = [];
        const functionRegex = /([a-z]+)\(/gi;
        let match;

        while ((match = functionRegex.exec(equation)) !== null) {
            const functionName = match[1].toLowerCase();
            if (!this.options.allowedFunctions.includes(functionName)) {
                errors.push(`Función no reconocida: ${functionName}`);
            }
        }

        return errors;
    }

    validateVariables(equation) {
        const errors = [];
        const variableRegex = /[a-z]/gi;
        let match;
        const foundVariables = new Set();

        while ((match = variableRegex.exec(equation)) !== null) {
            const variable = match[0].toLowerCase();

            // Ignorar variables que son parte de funciones
            const isInFunction = this.isPartOfFunction(equation, match.index);
            if (!isInFunction && !this.options.allowedVariables.includes(variable)) {
                if (!foundVariables.has(variable)) {
                    errors.push(`Variable no permitida: ${variable}`);
                    foundVariables.add(variable);
                }
            }
        }

        return errors;
    }

    isPartOfFunction(equation, index) {
        // Verificar si el carácter en el índice dado es parte de un nombre de función
        let start = index;
        while (start > 0 && /[a-z]/i.test(equation[start - 1])) {
            start--;
        }

        const potentialFunction = equation.substring(start, index + 1);
        return this.options.allowedFunctions.includes(potentialFunction.toLowerCase());
    }

    validateOperators(equation) {
        const errors = [];
        const operatorRegex = /[+\-*/^]{2,}/g;
        let match;

        while ((match = operatorRegex.exec(equation)) !== null) {
            // Permitir -- para números negativos, pero no otros operadores duplicados
            if (match[0] !== '--') {
                errors.push(`Operadores consecutivos no permitidos: ${match[0]}`);
            }
        }

        return errors;
    }

    showError(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'error-message active';
        this.input.classList.add('input-error');
        this.input.classList.remove('input-success');
    }

    showSuccess(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'success-message active';
        this.input.classList.remove('input-error');
        this.input.classList.add('input-success');
    }

    clearValidation() {
        this.errorContainer.textContent = '';
        this.errorContainer.className = '';
        this.input.classList.remove('input-error', 'input-success');
    }
}

class NumericValidator {
    constructor(inputElement, errorContainer, options = {}) {
        this.input = inputElement;
        this.errorContainer = errorContainer;
        this.options = Object.assign({
            min: null,
            max: null,
            integer: false,
            required: true,
            allowNegative: true
        }, options);

        this.setupValidation();
    }

    setupValidation() {
        this.input.addEventListener('input', this.validate.bind(this));
        this.input.addEventListener('blur', this.validate.bind(this));

        if (this.input.value) {
            setTimeout(() => this.validate(), 100);
        }
    }

    validate() {
        const value = this.input.value.trim();

        if (!value && this.options.required) {
            this.showError('Este campo es requerido');
            return false;
        }

        if (!value && !this.options.required) {
            this.clearValidation();
            return true;
        }

        // Validar formato numérico
        let num;
        if (this.options.integer) {
            num = parseInt(value);
            if (isNaN(num) || !Number.isInteger(num)) {
                this.showError('Por favor ingrese un número entero válido');
                return false;
            }
        } else {
            num = parseFloat(value);
            if (isNaN(num)) {
                this.showError('Por favor ingrese un número válido');
                return false;
            }
        }

        // Validar rango
        if (this.options.min !== null && num < this.options.min) {
            this.showError(`El valor debe ser mayor o igual a ${this.options.min}`);
            return false;
        }

        if (this.options.max !== null && num > this.options.max) {
            this.showError(`El valor debe ser menor o igual a ${this.options.max}`);
            return false;
        }

        // Validar signo
        if (!this.options.allowNegative && num < 0) {
            this.showError('El valor no puede ser negativo');
            return false;
        }

        this.showSuccess('Valor válido');
        return true;
    }

    showError(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'error-message active';
        this.input.classList.add('input-error');
        this.input.classList.remove('input-success');
    }

    showSuccess(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'success-message active';
        this.input.classList.remove('input-error');
        this.input.classList.add('input-success');
    }

    clearValidation() {
        this.errorContainer.textContent = '';
        this.errorContainer.className = '';
        this.input.classList.remove('input-error', 'input-success');
    }
}

class MatrixValidator {
    constructor(textareaElement, errorContainer, options = {}) {
        this.textarea = textareaElement;
        this.errorContainer = errorContainer;
        this.options = Object.assign({
            rows: null,
            cols: null,
            square: false
        }, options);

        this.setupValidation();
    }

    setupValidation() {
        this.textarea.addEventListener('input', this.validate.bind(this));
        this.textarea.addEventListener('blur', this.validate.bind(this));
    }

    validate() {
        const text = this.textarea.value.trim();

        if (!text) {
            this.showError('La matriz no puede estar vacía');
            return false;
        }

        const rows = text.split('\n').filter(row => row.trim() !== '');

        // Validar número de filas
        if (this.options.rows !== null && rows.length !== this.options.rows) {
            this.showError(`Se esperaban ${this.options.rows} filas, se encontraron ${rows.length}`);
            return false;
        }

        if (this.options.square && rows.length > 0) {
            const firstRowCols = rows[0].trim().split(/\s+/).length;
            if (rows.length !== firstRowCols) {
                this.showError(`La matriz debe ser cuadrada (${rows.length} filas × ${firstRowCols} columnas)`);
                return false;
            }
        }

        // Validar cada fila
        let expectedCols = null;
        for (let i = 0; i < rows.length; i++) {
            const elements = rows[i].trim().split(/\s+/);

            // Validar número de columnas
            if (expectedCols === null) {
                expectedCols = elements.length;
                if (this.options.cols !== null && expectedCols !== this.options.cols) {
                    this.showError(`Se esperaban ${this.options.cols} columnas, se encontraron ${expectedCols}`);
                    return false;
                }
            } else if (elements.length !== expectedCols) {
                this.showError(`Fila ${i + 1}: se esperaban ${expectedCols} elementos, se encontraron ${elements.length}`);
                return false;
            }

            // Validar que todos los elementos sean números
            for (let j = 0; j < elements.length; j++) {
                const num = parseFloat(elements[j]);
                if (isNaN(num)) {
                    this.showError(`Elemento [${i + 1},${j + 1}]: "${elements[j]}" no es un número válido`);
                    return false;
                }
            }
        }

        this.showSuccess('Matriz válida');
        return true;
    }

    showError(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'error-message active';
        this.textarea.classList.add('input-error');
        this.textarea.classList.remove('input-success');
    }

    showSuccess(message) {
        this.errorContainer.textContent = message;
        this.errorContainer.className = 'success-message active';
        this.textarea.classList.remove('input-error');
        this.textarea.classList.add('input-success');
    }
}

// Inicializar validadores en la página
document.addEventListener('DOMContentLoaded', function() {
    // Validadores de ecuaciones
    const equationInputs = document.querySelectorAll('.equation-input');
    equationInputs.forEach(input => {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-message';
        input.parentNode.appendChild(errorContainer);

        new EquationValidator(input, errorContainer);
    });

    // Validadores numéricos
    const numericInputs = document.querySelectorAll('.numeric-input');
    numericInputs.forEach(input => {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-message';
        input.parentNode.appendChild(errorContainer);

        const options = {
            min: input.dataset.min ? parseFloat(input.dataset.min) : null,
            max: input.dataset.max ? parseFloat(input.dataset.max) : null,
            integer: input.dataset.integer === 'true',
            allowNegative: input.dataset.allowNegative !== 'false'
        };

        new NumericValidator(input, errorContainer, options);
    });

    // Validadores de matrices
    const matrixInputs = document.querySelectorAll('.matrix-input');
    matrixInputs.forEach(textarea => {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-message';
        textarea.parentNode.appendChild(errorContainer);

        const options = {
            rows: textarea.dataset.rows ? parseInt(textarea.dataset.rows) : null,
            cols: textarea.dataset.cols ? parseInt(textarea.dataset.cols) : null,
            square: textarea.dataset.square === 'true'
        };

        new MatrixValidator(textarea, errorContainer, options);
    });
});