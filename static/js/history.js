/**
 * History: tabel data, pagination, filter tanggal
 */
(function () {
  const API_BASE = '';
  let currentPage = 1;
  const perPage = 20;
  let dateFrom = '';
  let dateTo = '';

  function buildQuery() {
    let q = '?page=' + currentPage + '&per_page=' + perPage;
    if (dateFrom) q += '&date_from=' + encodeURIComponent(dateFrom);
    if (dateTo) q += '&date_to=' + encodeURIComponent(dateTo);
    return q;
  }

  function statusClass(status) {
    if (!status) return '';
    const s = (status + '').toLowerCase();
    if (s.includes('prima')) return 'bg-green-100 text-green-800';
    if (s.includes('sedang')) return 'bg-yellow-100 text-yellow-800';
    if (s.includes('buruk')) return 'bg-red-100 text-red-800';
    return 'bg-slate-100 text-slate-800';
  }

  function formatDate(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleString('id-ID');
  }

  function renderTable(items) {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    if (!items || items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-slate-500">Tidak ada data.</td></tr>';
      return;
    }
    tbody.innerHTML = items.map(function (r) {
      return '<tr class="hover:bg-slate-50">' +
        '<td class="px-4 py-3 text-sm text-slate-800">' + r.id + '</td>' +
        '<td class="px-4 py-3 text-sm text-slate-800">' + Number(r.ph).toFixed(2) + '</td>' +
        '<td class="px-4 py-3 text-sm text-slate-800">' + Number(r.tds) + '</td>' +
        '<td class="px-4 py-3 text-sm text-slate-800">' + Number(r.suhu).toFixed(1) + '</td>' +
        '<td class="px-4 py-3"><span class="px-2 py-1 rounded text-xs font-medium ' + statusClass(r.status) + '">' + (r.status || '-') + '</span></td>' +
        '<td class="px-4 py-3 text-sm text-slate-600">' + formatDate(r.created_at) + '</td>' +
        '</tr>';
    }).join('');
  }

  function renderPagination(total, totalPages) {
    const container = document.getElementById('pagination-btns');
    if (!container) return;
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }
    let html = '';
    if (currentPage > 1) {
      html += '<button class="px-3 py-1 rounded border border-slate-300 text-sm hover:bg-slate-100" data-page="' + (currentPage - 1) + '">Sebelumnya</button>';
    }
    html += ' <span class="text-sm text-slate-600">Halaman ' + currentPage + ' / ' + totalPages + '</span> ';
    if (currentPage < totalPages) {
      html += '<button class="px-3 py-1 rounded border border-slate-300 text-sm hover:bg-slate-100" data-page="' + (currentPage + 1) + '">Selanjutnya</button>';
    }
    container.innerHTML = html;
    container.querySelectorAll('button[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        currentPage = parseInt(btn.getAttribute('data-page'), 10);
        load();
      });
    });
  }

  function updateInfo(total, page, perPage, totalPages) {
    const el = document.getElementById('history-info');
    if (el) el.textContent = 'Total ' + total + ' data';
  }

  function load() {
    const tbody = document.getElementById('history-tbody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-slate-500">Memuat...</td></tr>';
    fetch(API_BASE + '/api/history' + buildQuery())
      .then(function (r) { return r.json(); })
      .then(function (res) {
        renderTable(res.items);
        renderPagination(res.total, res.total_pages);
        updateInfo(res.total, res.page, res.per_page, res.total_pages);
      })
      .catch(function () {
        if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-red-500">Gagal memuat data.</td></tr>';
      });
  }

  document.getElementById('btn-filter')?.addEventListener('click', function () {
    dateFrom = document.getElementById('filter-date-from')?.value || '';
    dateTo = document.getElementById('filter-date-to')?.value || '';
    currentPage = 1;
    load();
  });

  load();
})();
