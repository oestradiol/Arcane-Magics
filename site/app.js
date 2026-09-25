(() => {
  const short = sha => typeof sha === 'string' ? sha.slice(0, 9) : 'unknown';
  const byId = id => document.getElementById(id);
  const table = byId('layer-table');
  const residualGrid = byId('residual-grid');

  const fallback = {
    root: {
      name: 'Root / The Machine', axis: 'map / territory',
      role: 'Routing and diachronic branch memory.',
      boundary: 'map != territory',
      residual: 'World or branch history can invalidate the current route.',
      reopening: 'handoff / merge memory -> revised Now Map',
      url: 'https://github.com/oestradiol/Arcane-Magics/tree/main'
    }
  };

  let snapshot = null;

  function selectPerspective(id, updateHash = true) {
    const layer = snapshot?.layers?.find(x => x.id === id) || fallback[id] || fallback.root;

    document.querySelectorAll('[data-perspective]').forEach(button => {
      const selected = button.dataset.perspective === id;
      button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      button.tabIndex = selected ? 0 : -1;
    });

    document.querySelectorAll('.layer-card').forEach(card => {
      card.toggleAttribute('data-current', card.dataset.layer === id);
    });

    byId('perspective-axis').textContent = (layer.axis || 'unknown').toUpperCase();
    byId('perspective-name').textContent = layer.name || id;
    byId('perspective-role').textContent = layer.role || 'Local repository function.';
    byId('perspective-boundary').textContent = layer.boundary || 'boundary not recorded';
    byId('perspective-residual').textContent = layer.residual || 'residual not recorded';
    byId('perspective-reopen').textContent = layer.reopening || 'reopening route not recorded';
    byId('perspective-sha').textContent = layer.commit ? short(layer.commit) : 'snapshot unavailable';
    byId('perspective-link').href = layer.url || '#';
    byId('perspective-link').textContent = 'Open ' + (layer.name || id) + ' on GitHub';

    if (updateHash && history.replaceState) {
      history.replaceState(null, '', '#perspective=' + encodeURIComponent(id));
    }
  }

  function renderResiduals(layers) {
    residualGrid.textContent = '';
    for (const layer of layers) {
      if (!layer.residual) continue;
      const article = document.createElement('article');
      article.className = 'bridge ' + (layer.residual_status === 'WITHHOLD' ? 'withheld' : 'open-bridge');

      const state = document.createElement('p');
      state.className = 'bridge-state';
      state.textContent = (layer.residual_status || 'OPEN') + ' · ' + layer.name;

      const title = document.createElement('h3');
      title.textContent = layer.residual_title || 'Future-separating distinction';

      const body = document.createElement('p');
      body.textContent = layer.residual;

      const link = document.createElement('a');
      link.href = layer.url;
      link.textContent = 'Open owning layer';

      article.append(state, title, body, link);
      residualGrid.appendChild(article);
    }
  }

  function renderSnapshot(data) {
    snapshot = data;
    byId('generated-at').textContent = 'snapshot: ' + new Date(data.generated_at).toLocaleString();

    const root = data.layers.find(x => x.id === 'root');
    if (root) byId('root-sha').textContent = 'root: ' + short(root.commit);

    for (const layer of data.layers) {
      const card = document.querySelector('[data-layer="' + layer.id + '"] [data-commit]');
      if (card) card.textContent = 'commit: ' + short(layer.commit);
    }

    table.textContent = '';
    for (const layer of data.layers) {
      const tr = document.createElement('tr');
      for (const value of [layer.name, layer.branch, short(layer.commit), layer.axis]) {
        const td = document.createElement('td');
        td.textContent = value;
        tr.appendChild(td);
      }
      table.appendChild(tr);
    }

    renderResiduals(data.layers);

    const requested = location.hash.startsWith('#perspective=')
      ? decodeURIComponent(location.hash.slice('#perspective='.length))
      : 'root';
    selectPerspective(data.layers.some(x => x.id === requested) ? requested : 'root', false);
  }

  document.querySelectorAll('[data-perspective]').forEach(button => {
    button.addEventListener('click', () => selectPerspective(button.dataset.perspective));
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      const buttons = [...document.querySelectorAll('[data-perspective]')];
      const current = buttons.indexOf(event.currentTarget);
      const delta = event.key === 'ArrowRight' ? 1 : -1;
      const next = buttons[(current + delta + buttons.length) % buttons.length];
      next.focus();
      selectPerspective(next.dataset.perspective);
    });
  });

  document.querySelectorAll('[data-select-layer]').forEach(link => {
    link.addEventListener('click', () => selectPerspective(link.dataset.selectLayer));
  });

  fetch('./data/layers.json', {cache: 'no-store'})
    .then(r => {
      if (!r.ok) throw new Error('snapshot unavailable');
      return r.json();
    })
    .then(renderSnapshot)
    .catch(() => {
      byId('generated-at').textContent = 'snapshot unavailable';
      table.innerHTML = '<tr><td colspan="4">Build snapshot unavailable. GitHub remains the source of branch truth.</td></tr>';
      selectPerspective('root', false);
    });
})();
