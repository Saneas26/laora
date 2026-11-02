/* Pie común del Grupo Saneas en laOra (orden de Óscar, 02/11/2026).
   El componente es el mismo de todas las casas: no se toca aquí. */
(function () {
  if (!window.GrupoSaneas) return;
  GrupoSaneas.init({ actual: 'laora', logos: '/assets/grupo/', barra: 'header' });
  var estilo = document.createElement('style');
  estilo.textContent = '#pieGrupo{background:#090909;padding:40px 20px 48px;border-top:1px solid #2a2a2a}'
    + '#pieGrupo h2{margin:0 auto 20px;max-width:1100px;font:600 15px/1.3 Inter,system-ui,sans-serif;'
    + 'letter-spacing:.08em;text-transform:uppercase;color:#D4A94B}'
    + '#pieGrupo .gs-grid{max-width:1100px;margin:0 auto}'
    + '#pieGrupo .gs-item b{color:#F7F7F5}';
  document.head.appendChild(estilo);
  var pie = document.createElement('section');
  pie.id = 'pieGrupo';
  pie.setAttribute('aria-label', 'Grupo Saneas');
  pie.innerHTML = '<h2>Grupo Saneas</h2>' + GrupoSaneas.gridHTML();
  // Seis páginas traían una rejilla hecha a mano: la común ocupa su sitio.
  var vieja = document.querySelector('.gp-grid');
  if (vieja) {
    var rotulo = vieja.previousElementSibling;
    if (rotulo && rotulo.classList.contains('fg-title')) rotulo.remove();
    pie.style.borderTop = '0';
    pie.style.background = 'none';
    vieja.parentNode.replaceChild(pie, vieja);
  } else {
    document.body.appendChild(pie);
  }
})();
