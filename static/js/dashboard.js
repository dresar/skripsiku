/**
 * Dashboard: realtime cards, WebSocket, grafik 30 data terakhir
 */
(function () {
  const WS_URL = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/realtime';
  const API_BASE = '';

  let chart = null;
  const maxChartPoints = 30;

  function statusClass(status) {
    if (!status) return 'bg-slate-200 text-slate-700';
    const s = (status + '').toLowerCase();
    if (s.includes('prima')) return 'bg-green-500 text-white';
    if (s.includes('sedang')) return 'bg-yellow-500 text-slate-800';
    if (s.includes('buruk')) return 'bg-red-500 text-white';
    return 'bg-slate-200 text-slate-700';
  }

  function updateCards(data) {
    document.getElementById('card-ph').textContent = data.ph != null ? Number(data.ph).toFixed(2) : '--';
    document.getElementById('card-tds').textContent = data.tds != null ? Number(data.tds) : '--';
    document.getElementById('card-suhu').textContent = data.suhu != null ? Number(data.suhu).toFixed(1) : '--';
    const statusEl = document.getElementById('card-status');
    statusEl.textContent = data.status || '--';
    statusEl.className = 'text-lg font-bold mt-1 px-3 py-1 rounded-lg inline-block ' + statusClass(data.status);
  }

  function updateWsIndicator(connected) {
    const el = document.getElementById('ws-indicator');
    if (!el) return;
    el.classList.remove('bg-amber-400', 'bg-green-500', 'animate-pulse');
    if (connected) {
      el.classList.add('bg-green-500');
      el.title = 'Connected';
    } else {
      el.classList.add('bg-amber-400', 'animate-pulse');
      el.title = 'Connecting...';
    }
  }

  function ensureChart(labels, phData, tdsData, suhuData) {
    const ctx = document.getElementById('chart-realtime');
    if (!ctx) return;
    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = phData;
      chart.data.datasets[1].data = tdsData;
      chart.data.datasets[2].data = suhuData;
      chart.update('none');
      return;
    }
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'pH', data: phData, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', tension: 0.3, yAxisID: 'y' },
          { label: 'TDS', data: tdsData, borderColor: '#8b5cf6', backgroundColor: 'rgba(139,92,246,0.1)', tension: 0.3, yAxisID: 'y1' },
          { label: 'Suhu (°C)', data: suhuData, borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)', tension: 0.3, yAxisID: 'y2' }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          y: { type: 'linear', display: true, position: 'left', min: 0, max: 14, title: { display: true, text: 'pH' } },
          y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'TDS' } },
          y2: { type: 'linear', display: false }
        }
      }
    });
  }

  function buildChartFromHistory(items) {
    items = (items || []).slice(0, maxChartPoints).reverse();
    const labels = items.map(function (r) {
      const t = r.created_at ? new Date(r.created_at) : null;
      return t ? t.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '';
    });
    const phData = items.map(function (r) { return r.ph; });
    const tdsData = items.map(function (r) { return r.tds; });
    const suhuData = items.map(function (r) { return r.suhu; });
    ensureChart(labels, phData, tdsData, suhuData);
  }

  function fetchLatest() {
    fetch(API_BASE + '/api/latest')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        updateCards(data);
      })
      .catch(function () {});
  }

  function fetchHistoryForChart() {
    fetch(API_BASE + '/api/history?per_page=' + maxChartPoints + '&page=1')
      .then(function (r) { return r.json(); })
      .then(function (res) {
        buildChartFromHistory(res.items || []);
      })
      .catch(function () {});
  }

  // WebSocket
  let ws = null;
  function connectWs() {
    ws = new WebSocket(WS_URL);
    ws.onopen = function () { updateWsIndicator(true); };
    ws.onclose = function () {
      updateWsIndicator(false);
      setTimeout(connectWs, 3000);
    };
    ws.onerror = function () {};
    ws.onmessage = function (ev) {
      try {
        const data = JSON.parse(ev.data);
        if (data.ph != null || data.tds != null || data.suhu != null) {
          updateCards(data);
          fetchHistoryForChart();
        }
      } catch (e) {}
    };
  }

  fetchLatest();
  fetchHistoryForChart();
  connectWs();
})();
