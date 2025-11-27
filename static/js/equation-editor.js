class EquationEditor {
    constructor(inputElement, suggestionsContainer) {
        this.input = inputElement;
        this.suggestionsContainer = suggestionsContainer;
        this.functions = [
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'sinh', 'cosh', 'tanh', 'exp', 'log', 'ln', 
            'sqrt', 'abs', 'pi', 'e'
        ];
        this.operators = ['+', '-', '*', '/', '^', '(', ')'];
        this.variables = ['x', 'y', 't', 'z'];
        
        this.setupAutocomplete();
        this.setupKeyboardShortcuts();
    }

    setupAutocomplete() {
        this.input.addEventListener('input', this.handleAutocomplete.bind(this));
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
        this.input.addEventListener('focus', this.showSuggestions.bind(this));
    }

    setupKeyboardShortcuts() {
        this.input.addEventListener('keydown', (e) => {
            // Ctrl + Espacio para forzar autocompletado
            if (e.ctrlKey && e.code === 'Space') {
                e.preventDefault();
                this.showSuggestions();
            }
            
            // Tab para completar la primera sugerencia
            if (e.key === 'Tab' && this.suggestionsContainer.style.display === 'block') {
                e.preventDefault();
                this.selectFirstSuggestion();
            }
        });
    }

    handleAutocomplete(event) {
        const value = this.input.value;
        const cursorPosition = this.input.selectionStart;
        
        // Obtener la palabra actual alrededor del cursor
        const currentWord = this.getCurrentWord(value, cursorPosition);
        
        if (currentWord && currentWord.length > 0) {
            const matches = this.getMatches(currentWord);
            this.showSuggestions(matches, currentWord);
        } else {
            this.hideSuggestions();
        }
    }

    getCurrentWord(text, cursorPosition) {
        // Encontrar el inicio de la palabra actual
        let start = cursorPosition - 1;
        while (start >= 0 && this.isWordCharacter(text.charAt(start))) {
            start--;
        }
        start++;
        
        // Encontrar el final de la palabra actual
        let end = cursorPosition;
        while (end < text.length && this.isWordCharacter(text.charAt(end))) {
            end++;
        }
        
        return text.substring(start, end);
    }

    isWordCharacter(char) {
        return /[a-zA-Z0-9_]/.test(char);
    }

    getMatches(currentWord) {
        const allOptions = [...this.functions, ...this.variables];
        return allOptions.filter(option => 
            option.toLowerCase().startsWith(currentWord.toLowerCase())
        );
    }

    showSuggestions(matches = null, currentWord = '') {
        if (!matches) {
            // Mostrar todas las funciones si no hay coincidencias específicas
            matches = this.functions;
        }

        if (matches.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsContainer.innerHTML = '';
        this.suggestionsContainer.style.display = 'block';

        matches.forEach(match => {
            const suggestion = document.createElement('div');
            suggestion.className = 'suggestion-item';
            suggestion.innerHTML = this.highlightMatch(match, currentWord);
            suggestion.dataset.value = match;
            
            suggestion.addEventListener('click', () => {
                this.selectSuggestion(match, currentWord);
            });
            
            this.suggestionsContainer.appendChild(suggestion);
        });

        this.positionSuggestions();
    }

    highlightMatch(match, currentWord) {
        if (!currentWord) return match;
        
        const index = match.toLowerCase().indexOf(currentWord.toLowerCase());
        if (index === -1) return match;
        
        return match.substring(0, index) + 
               '<strong>' + match.substring(index, index + currentWord.length) + '</strong>' +
               match.substring(index + currentWord.length);
    }

    positionSuggestions() {
        const rect = this.input.getBoundingClientRect();
        this.suggestionsContainer.style.position = 'absolute';
        this.suggestionsContainer.style.left = rect.left + 'px';
        this.suggestionsContainer.style.top = (rect.bottom + window.scrollY) + 'px';
        this.suggestionsContainer.style.width = rect.width + 'px';
    }

    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
    }

    selectFirstSuggestion() {
        const firstSuggestion = this.suggestionsContainer.querySelector('.suggestion-item');
        if (firstSuggestion) {
            this.selectSuggestion(firstSuggestion.dataset.value, '');
        }
    }

    selectSuggestion(suggestion, currentWord) {
        const value = this.input.value;
        const cursorPosition = this.input.selectionStart;
        
        // Encontrar los límites de la palabra actual
        const wordStart = cursorPosition - currentWord.length;
        const wordEnd = cursorPosition;
        
        // Reemplazar la palabra actual con la sugerencia
        const newValue = value.substring(0, wordStart) + suggestion + value.substring(wordEnd);
        this.input.value = newValue;
        
        // Posicionar el cursor después de la función y agregar paréntesis si es necesario
        const newCursorPosition = wordStart + suggestion.length;
        if (this.functions.includes(suggestion)) {
            this.input.value = newValue + '()';
            this.input.setSelectionRange(newCursorPosition + 1, newCursorPosition + 1);
        } else {
            this.input.setSelectionRange(newCursorPosition, newCursorPosition);
        }
        
        this.hideSuggestions();
        this.input.focus();
        
        // Disparar eventos para validación
        this.input.dispatchEvent(new Event('input'));
        this.input.dispatchEvent(new Event('change'));
    }

    handleKeyDown(event) {
        if (event.key === 'ArrowDown' && this.suggestionsContainer.style.display === 'block') {
            event.preventDefault();
            this.navigateSuggestions(1);
        } else if (event.key === 'ArrowUp' && this.suggestionsContainer.style.display === 'block') {
            event.preventDefault();
            this.navigateSuggestions(-1);
        } else if (event.key === 'Escape') {
            this.hideSuggestions();
        }
    }

    navigateSuggestions(direction) {
        const suggestions = Array.from(this.suggestionsContainer.querySelectorAll('.suggestion-item'));
        const active = this.suggestionsContainer.querySelector('.suggestion-active');
        
        let index = active ? suggestions.indexOf(active) : -1;
        index = (index + direction + suggestions.length) % suggestions.length;
        
        if (active) active.classList.remove('suggestion-active');
        suggestions[index].classList.add('suggestion-active');
    }

    // Método para insertar caracteres desde el teclado virtual
    insertText(text) {
        const start = this.input.selectionStart;
        const end = this.input.selectionEnd;
        const value = this.input.value;
        
        this.input.value = value.substring(0, start) + text + value.substring(end);
        
        // Posicionar el cursor después del texto insertado
        const newPosition = start + text.length;
        this.input.setSelectionRange(newPosition, newPosition);
        this.input.focus();
        
        // Disparar eventos
        this.input.dispatchEvent(new Event('input'));
        this.input.dispatchEvent(new Event('change'));
    }

    // Método para limpiar el campo
    clear() {
        this.input.value = '';
        this.hideSuggestions();
        this.input.focus();
        this.input.dispatchEvent(new Event('input'));
    }

    // Método para eliminar un carácter
    deleteChar() {
        const start = this.input.selectionStart;
        const end = this.input.selectionEnd;
        const value = this.input.value;
        
        if (start === end && start > 0) {
            // Eliminar carácter antes del cursor
            this.input.value = value.substring(0, start - 1) + value.substring(end);
            this.input.setSelectionRange(start - 1, start - 1);
        } else if (start !== end) {
            // Eliminar texto seleccionado
            this.input.value = value.substring(0, start) + value.substring(end);
            this.input.setSelectionRange(start, start);
        }
        
        this.input.focus();
        this.input.dispatchEvent(new Event('input'));
    }
}

// Inicializar todos los editores de ecuación en la página
document.addEventListener('DOMContentLoaded', function() {
    const equationInputs = document.querySelectorAll('.equation-input');
    
    equationInputs.forEach(input => {
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'equation-suggestions';
        input.parentNode.appendChild(suggestionsContainer);
        
        new EquationEditor(input, suggestionsContainer);
    });
});