document.addEventListener('DOMContentLoaded', function () {
  // Trigger shake animation if there's an error message on the page
  const errorMessages = document.querySelectorAll('[style*="#661111"], [style*="#f8d7da"]');
  if (errorMessages.length > 0) {
    const form = document.querySelector('.form, .requests-container');
    if (form) {
      form.classList.add('shake');
      // Remove the class after animation completes so it can be triggered again
      setTimeout(() => form.classList.remove('shake'), 500);
    }
  }
  
  // Floating label behavior (include textarea)
  const inputs = document.querySelectorAll('.field-wrap input, .field-wrap textarea');
  // Initialize labels for pre-filled fields
  inputs.forEach((fld) => {
    const initLabel = fld.previousElementSibling;
    if (initLabel && fld.value) initLabel.classList.add('active');
  });

  inputs.forEach((input) => {
    // Strip non-digit characters for numeric inputs as the user types
    input.addEventListener('input', () => {
      // Only apply numeric cleaning to INPUT elements (not textarea)
      if (input.tagName === 'INPUT') {
        const isNumeric = input.getAttribute('inputmode') === 'numeric' || input.type === 'number' || input.name === 'employee_id';
        if (isNumeric) {
          const cleaned = input.value.replace(/\D+/g, '');
          if (cleaned !== input.value) {
            const pos = input.selectionStart - (input.value.length - cleaned.length);
            input.value = cleaned;
            // restore caret position
            try {
              input.setSelectionRange(Math.max(0, pos), Math.max(0, pos));
            } catch (e) {
              /* ignore if selection not supported */
            }
          }
        }
      }
      // keep floating label in sync on input/textarea
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

  // Simple client-side submit handling for demo-only forms
  // If a form has the attribute `data-demo`, intercept submit and show an alert.
  // Otherwise allow normal form submission to the server (sign-in and PTO forms).
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', (e) => {
      const isDemo = form.hasAttribute('data-demo');
      if (!isDemo) return; // allow actual submit for non-demo forms

      e.preventDefault(); // prevent actual submit in demo
      const data = Array.from(new FormData(form).entries())
        .map(([k, v]) => `${k}: ${v}`)
        .join('\n');
      alert('Form submitted (demo)\n\n' + data);
    });
  });

  // JS fallback to forcibly set textarea color (workaround for stubborn autofill styles)
  function forceTextareaColor() {
    const textareas = document.querySelectorAll('.form textarea, .field-wrap textarea, textarea#reason');
    textareas.forEach((t) => {
      // inline styles have higher precedence than many stylesheet rules
      t.style.color = '#ffffff';
      t.style.backgroundColor = t.style.backgroundColor || 'transparent';
      // vendor fill color (some browsers honor this when set inline)
      t.style.setProperty('-webkit-text-fill-color', '#ffffff', 'important');
      t.style.setProperty('transition', 'color 0.01s linear');
    });
  }

  // Run immediately and a few times after load to catch delayed autofill application
  forceTextareaColor();
  setTimeout(forceTextareaColor, 100);
  setTimeout(forceTextareaColor, 500);
  setTimeout(forceTextareaColor, 1500);

  // Re-apply when focus/blur happens on textareas (some browsers re-style on focus)
  document.addEventListener('focusin', (e) => {
    if (e.target && e.target.tagName === 'TEXTAREA') forceTextareaColor();
  });

  // Some browsers dispatch an animationstart when autofill triggers; use it if available
  document.addEventListener('animationstart', (e) => {
    // animationName can vary by UA; we just reapply on any animationstart as a safe fallback
    if (e && e.srcElement && (e.animationName || '').toLowerCase().includes('auto')) {
      forceTextareaColor();
    }
  }, true);
});