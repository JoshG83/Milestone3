document.addEventListener('DOMContentLoaded', function () {
  // Floating label behavior
  const inputs = document.querySelectorAll('.field-wrap input');
  inputs.forEach((input) => {
    // Strip non-digit characters for numeric fields as the user types
    input.addEventListener('input', () => {
      const isNumeric = input.getAttribute('inputmode') === 'numeric' || input.type === 'number' || input.name === 'employee_id';
      if (isNumeric) {
        const cleaned = input.value.replace(/\D+/g, '');
        if (cleaned !== input.value) {
          const pos = input.selectionStart - (input.value.length - cleaned.length);
          input.value = cleaned;
          // restore caret position
          input.setSelectionRange(Math.max(0, pos), Math.max(0, pos));
        }
      }
      // keep floating label in sync on input
      const label = input.previousElementSibling;
      if (label) {
        if (input.value) label.classList.add('active', 'highlight');
        else label.classList.remove('active', 'highlight');
      }
    });

    input.addEventListener('focus', () => {
      const label = input.previousElementSibling;
      if (label) label.classList.add('active');
    });
    input.addEventListener('blur', () => {
      const label = input.previousElementSibling;
      if (label && !input.value) label.classList.remove('active');
    });
  });

  // Simple client-side submit handling for demo
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault(); // prevent actual submit in demo
      const data = Array.from(new FormData(form).entries())
        .map(([k,v]) => `${k}: ${v}`)
        .join('\n');
      alert('Form submitted (demo)\n\n' + data);
    });
  });
});