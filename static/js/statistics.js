/**
 * Statistics: rata-rata, total, status dominan, grafik distribusi status
 */
(function () {
  const API_BASE = '';

  function statusClass(status) {
    if (!status) return 'bg-slate-200 text-slate-700';
    const s = (status + '').toLowerCase();
    if (s.includes('prima')) return 'bg-green-500 text-white';
    if (s.includes('sedang')) return 'bg-yellow-500 text-slate-800';
    if (s.includes('buruk')) return 'bg-red-500 text-white';
    return 'bg-slate-200 text-slate-700';
  }

  function load() {
    fetch(API_BASE + '/api/statistics')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        document.getElementById('stat-avg-ph').textContent = data.avg_ph != null ? Number(data.avg_ph).toFixed(2) : '--';
        document.getElementById('stat-avg-tds').textContent = data.avg_tds != null ? Number(data.avg_tds).toFixed(0) : '--';
        document.getElementById('stat-total').textContent = data.total_readings != null ? data.total_readings : '--';
        const dominantEl = document.getElementById('stat-dominant');
        dominantEl.textContent = data.dominant_status || '--';
        dominantEl.className = 'text-lg font-bold mt-1 px-3 py-1 rounded-lg inline-block ' + statusClass(data.dominant_status);

        const counts = data.status_counts || {};
        const labels = Object.keys(counts);
        const values = labels.map(function (k) { return counts[k]; });
        const colors = labels.map(function (k) {
          const s = (k + '').toLowerCase();
          if (s.includes('prima')) return '#22c55e';
          if (s.includes('sedang')) return '#eab308';
          if (s.includes('buruk')) return '#ef4444';
          return '#94a3b8';
        });
        const ctx = document.getElementById('chart-status');
        if (ctx && labels.length > 0) {
          new Chart(ctx, {
            type: 'doughnut',
            data: {
              labels: labels,
              datasets: [{ data: values, backgroundColor: colors, borderWidth: 2 }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { position: 'bottom' } }
            }
          });
        } else if (ctx) {
          ctx.parentElement.innerHTML = '<p class="text-slate-500 text-center py-8">Belum ada data untuk statistik.</p>';
        }
      })
      .catch(function () {
        document.getElementById('stat-avg-ph').textContent = '--';
        document.getElementById('stat-avg-tds').textContent = '--';
        document.getElementById('stat-total').textContent = '--';
        document.getElementById('stat-dominant').textContent = '--';
      });
  }

  load();
})();
