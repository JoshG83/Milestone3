document.addEventListener('DOMContentLoaded', function () {
  // Floating label behavior
  const inputs = document.querySelectorAll('.field-wrap input');
  inputs.forEach((input) => {
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