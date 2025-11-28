class MathKeyboard {
    constructor(container, targetInput) {
        this.container = container;
        this.targetInput = targetInput;
        this.isVisible = false;

        this.initializeKeyboard();
        this.setupEventListeners();
    }

    initializeKeyboard() {
        this.container.innerHTML = '';
        this.container.className = 'math-keyboard';

        const keyboardLayout = this.createKeyboardLayout();
        this.container.appendChild(keyboardLayout);
    }

    createKeyboardLayout() {
        const keyboard = document.createElement('div');
        keyboard.className = 'keyboard-layout';

        // Primera fila: funciones avanzadas
        const row1 = this.createRow([
            { type: 'function', label: 'sin', value: 'sin()', class: 'func-btn' },
            { type: 'function', label: 'cos', value: 'cos()', class: 'func-btn' },
            { type: 'function', label: 'tan', value: 'tan()', class: 'func-btn' },
            { type: 'function', label: 'asin', value: 'asin()', class: 'func-btn' },
            { type: 'function', label: 'acos', value: 'acos()', class: 'func-btn' },
            { type: 'function', label: 'atan', value: 'atan()', class: 'func-btn' },
            { type: 'action', label: 'DEL', value: 'delete', class: 'action-btn delete' },
            { type: 'action', label: 'AC', value: 'clear', class: 'action-btn clear' }
        ]);

        // Segunda fila: más funciones
        const row2 = this.createRow([
            { type: 'function', label: 'sinh', value: 'sinh()', class: 'func-btn' },
            { type: 'function', label: 'cosh', value: 'cosh()', class: 'func-btn' },
            { type: 'function', label: 'tanh', value: 'tanh()', class: 'func-btn' },
            { type: 'function', label: 'exp', value: 'exp()', class: 'func-btn' },
            { type: 'function', label: 'log', value: 'log()', class: 'func-btn' },
            { type: 'function', label: 'ln', value: 'ln()', class: 'func-btn' },
            { type: 'function', label: '√', value: 'sqrt()', class: 'func-btn' },
            { type: 'function', label: 'abs', value: 'abs()', class: 'func-btn' }
        ]);

        // Tercera fila: números y operadores básicos
        const row3 = this.createRow([
            { type: 'number', label: '7', value: '7', class: 'num-btn' },
            { type: 'number', label: '8', value: '8', class: 'num-btn' },
            { type: 'number', label: '9', value: '9', class: 'num-btn' },
            { type: 'operator', label: '(', value: '(', class: 'op-btn' },
            { type: 'operator', label: ')', value: ')', class: 'op-btn' },
            { type: 'operator', label: '^', value: '^', class: 'op-btn' },
            { type: 'constant', label: 'π', value: 'pi', class: 'const-btn' },
            { type: 'constant', label: 'e', value: 'e', class: 'const-btn' }
        ]);

        // Cuarta fila: números y operadores
        const row4 = this.createRow([
            { type: 'number', label: '4', value: '4', class: 'num-btn' },
            { type: 'number', label: '5', value: '5', class: 'num-btn' },
            { type: 'number', label: '6', value: '6', class: 'num-btn' },
            { type: 'operator', label: '+', value: '+', class: 'op-btn' },
            { type: 'operator', label: '-', value: '-', class: 'op-btn' },
            { type: 'variable', label: 'x', value: 'x', class: 'var-btn' },
            { type: 'variable', label: 'y', value: 'y', class: 'var-btn' },
            { type: 'variable', label: 't', value: 't', class: 'var-btn' }
        ]);

        // Quinta fila: números y operadores
        const row5 = this.createRow([
            { type: 'number', label: '1', value: '1', class: 'num-btn' },
            { type: 'number', label: '2', value: '2', class: 'num-btn' },
            { type: 'number', label: '3', value: '3', class: 'num-btn' },
            { type: 'operator', label: '*', value: '*', class: 'op-btn' },
            { type: 'operator', label: '/', value: '/', class: 'op-btn' },
            { type: 'number', label: '.', value: '.', class: 'num-btn' },
            { type: 'number', label: '0', value: '0', class: 'num-btn' },
            { type: 'action', label: '⏎', value: 'enter', class: 'action-btn enter' }
        ]);

        keyboard.appendChild(row1);
        keyboard.appendChild(row2);
        keyboard.appendChild(row3);
        keyboard.appendChild(row4);
        keyboard.appendChild(row5);

        return keyboard;
    }

    createRow(buttons) {
        const row = document.createElement('div');
        row.className = 'keyboard-row';

        buttons.forEach(buttonConfig => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `keyboard-button ${buttonConfig.class}`;
            button.textContent = buttonConfig.label;
            button.dataset.type = buttonConfig.type;
            button.dataset.value = buttonConfig.value;

            button.addEventListener('click', () => {
                this.handleButtonClick(buttonConfig);
            });

            row.appendChild(button);
        });

        return row;
    }

    handleButtonClick(buttonConfig) {
        if (!this.targetInput) return;

        switch (buttonConfig.type) {
            case 'number':
            case 'operator':
            case 'variable':
            case 'constant':
                this.insertText(buttonConfig.value);
                break;

            case 'function':
                this.insertFunction(buttonConfig.value);
                break;

            case 'action':
                this.handleAction(buttonConfig.value);
                break;
        }

        // Disparar eventos de input para validación
        this.targetInput.dispatchEvent(new Event('input'));
        this.targetInput.dispatchEvent(new Event('change'));
        this.targetInput.focus();
    }

    insertText(text) {
        const start = this.targetInput.selectionStart;
        const end = this.targetInput.selectionEnd;
        const value = this.targetInput.value;

        this.targetInput.value = value.substring(0, start) + text + value.substring(end);
        this.targetInput.setSelectionRange(start + text.length, start + text.length);
    }

    insertFunction(func) {
        const start = this.targetInput.selectionStart;
        const end = this.targetInput.selectionEnd;
        const value = this.targetInput.value;

        this.targetInput.value = value.substring(0, start) + func + value.substring(end);

        // Posicionar cursor dentro de los paréntesis
        const cursorPos = start + func.indexOf('(') + 1;
        this.targetInput.setSelectionRange(cursorPos, cursorPos);
    }

    handleAction(action) {
        switch (action) {
            case 'delete':
                this.deleteChar();
                break;

            case 'clear':
                this.targetInput.value = '';
                break;

            case 'enter':
                this.hide();
                break;
        }
    }

    deleteChar() {
        const start = this.targetInput.selectionStart;
        const end = this.targetInput.selectionEnd;
        const value = this.targetInput.value;

        if (start === end && start > 0) {
            // Eliminar carácter antes del cursor
            this.targetInput.value = value.substring(0, start - 1) + value.substring(end);
            this.targetInput.setSelectionRange(start - 1, start - 1);
        } else if (start !== end) {
            // Eliminar texto seleccionado
            this.targetInput.value = value.substring(0, start) + value.substring(end);
            this.targetInput.setSelectionRange(start, start);
        }
    }

    show(inputElement = null) {
        if (inputElement) {
            this.targetInput = inputElement;
        }

        if (!this.targetInput) return;

        this.container.style.display = 'block';
        this.isVisible = true;

        // Posicionar el teclado cerca del input
        this.positionKeyboard();
    }

    hide() {
        this.container.style.display = 'none';
        this.isVisible = false;
    }

    toggle(inputElement = null) {
        if (inputElement) {
            this.targetInput = inputElement;
        }

        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    positionKeyboard() {
        if (!this.targetInput) return;

        const rect = this.targetInput.getBoundingClientRect();
        this.container.style.position = 'fixed';
        this.container.style.left = '50%';
        this.container.style.bottom = '20px';
        this.container.style.transform = 'translateX(-50%)';
        this.container.style.zIndex = '1000';
    }

    setupEventListeners() {
        // Cerrar teclado al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target) &&
                e.target !== this.targetInput &&
                !e.target.classList.contains('keyboard-toggle')) {
                this.hide();
            }
        });

        // Tecla Escape para cerrar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                this.hide();
            }
        });
    }
}

// Inicializar teclado virtual
document.addEventListener('DOMContentLoaded', function() {
    const keyboardContainer = document.createElement('div');
    keyboardContainer.id = 'virtual-keyboard';
    document.body.appendChild(keyboardContainer);

    const mathKeyboard = new MathKeyboard(keyboardContainer);

    // Agregar botones de toggle a los inputs de ecuación
    const equationInputs = document.querySelectorAll('.equation-input');
    equationInputs.forEach(input => {
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'keyboard-toggle';
        toggleBtn.innerHTML = '⌨️';
        toggleBtn.title = 'Abrir teclado virtual';

        toggleBtn.addEventListener('click', () => {
            mathKeyboard.toggle(input);
        });

        // Insertar después del input
        input.parentNode.insertBefore(toggleBtn, input.nextSibling);
    });

    // También mostrar teclado al enfocar el input en dispositivos táctiles
    if ('ontouchstart' in window) {
        equationInputs.forEach(input => {
            input.addEventListener('focus', () => {
                mathKeyboard.show(input);
            });
        });
    }
});