(() => {
  const short = sha => typeof sha === 'string' ? sha.slice(0, 9) : 'unknown';
  const table = document.getElementById('layer-table');

  fetch('./data/layers.json', {cache: 'no-store'})
    .then(r => {
      if (!r.ok) throw new Error('snapshot unavailable');
      return r.json();
    })
    .then(data => {
      document.getElementById('generated-at').textContent = 'snapshot: ' + new Date(data.generated_at).toLocaleString();
      const root = data.layers.find(x => x.id === 'root');
      if (root) document.getElementById('root-sha').textContent = 'root: ' + short(root.commit);

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
    })
    .catch(() => {
      document.getElementById('generated-at').textContent = 'snapshot unavailable';
      table.innerHTML = '<tr><td colspan="4">Build snapshot unavailable. GitHub remains the source of branch truth.</td></tr>';
    });
})();
