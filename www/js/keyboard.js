
console.log("keyboard.js cargado ✅");

document.addEventListener("click", function (event) {
  // ¿Se hizo click en una tecla?
  const key = event.target.closest(".math-key");
  if (!key) return;

  // Input de la ecuación
  const input = document.getElementById("equation_input");
  if (!input) {
    console.warn("No se encontró #equation_input");
    return;
  }

  const value = key.dataset.value || key.textContent || "";

  const start = input.selectionStart ?? input.value.length;
  const end = input.selectionEnd ?? input.value.length;

  const before = input.value.slice(0, start);
  const after = input.value.slice(end);

  input.value = before + value + after;

  const newPos = start + value.length;
  input.focus();
  input.setSelectionRange(newPos, newPos);

  const ev = new Event("input", { bubbles: true });
  input.dispatchEvent(ev);

  console.log(`Tecla pulsada: "${value}" → nuevo valor: "${input.value}"`);
});
