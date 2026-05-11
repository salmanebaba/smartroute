/* ═══════════════════════════════════════════════════════
   GreenTech SmartBin — Dashboard App Logic
   ═══════════════════════════════════════════════════════ */

// ── Configuration ─────────────────────────────────────
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '0.0.0.0'
  ? 'http://localhost:8000'
  : window.location.origin.replace(':8080', ':8000');

const REFRESH_INTERVAL = 30000; // 30s auto-refresh
const MAP_CENTER = [33.9770, -6.8660];
const MAP_ZOOM = 14;

// ── State ─────────────────────────────────────────────
let map;
let binMarkers = {};
let routeLines = [];
let currentStrategy = 'fill_level';
let binsData = [];
let chartInstance = null;
let chartsCollapsed = false;
let currentChartTab = 'trend';

// ── Initialize ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadDashboard();
  setupEventListeners();
  setInterval(loadDashboard, REFRESH_INTERVAL);
});

// ── Map ───────────────────────────────────────────────
function initMap() {
  map = L.map('map', {
    center: MAP_CENTER,
    zoom: MAP_ZOOM,
    zoomControl: false,
  });

  L.control.zoom({ position: 'bottomleft' }).addTo(map);

  // Dark map tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);
}

// ── Data Loading ──────────────────────────────────────
async function loadDashboard() {
  try {
    const [binsRes, routeRes, statsRes] = await Promise.all([
      fetch(`${API_BASE}/api/bins`),
      fetch(`${API_BASE}/api/route?strategy=${currentStrategy}`),
      fetch(`${API_BASE}/api/stats`),
    ]);
    binsData = await binsRes.json();
    const routeData = await routeRes.json();
    const statsData = await statsRes.json();

    renderBins(binsData, routeData);
    renderRoute(routeData);
    renderKPIs(statsData, routeData);
    renderBinList(binsData, routeData);
    loadChartData();
  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

// ── Render Bins on Map ────────────────────────────────
function renderBins(bins, routeData) {
  // Clear existing markers
  Object.values(binMarkers).forEach(m => map.removeLayer(m));
  binMarkers = {};

  const orderMap = {};
  if (routeData && routeData.ordered_bin_ids) {
    routeData.ordered_bin_ids.forEach((id, i) => { orderMap[id] = i + 1; });
  }

  bins.forEach(bin => {
    const status = bin.fill_level >= 80 ? 'critical' : bin.fill_level >= 50 ? 'warning' : 'normal';
    const order = orderMap[bin.id];

    const html = `
      <div class="bin-marker">
        <div class="bin-marker__circle ${status}">${bin.fill_level}%</div>
        ${order ? `<div class="bin-marker__order">${order}</div>` : ''}
      </div>`;

    const icon = L.divIcon({ html, className: '', iconSize: [40, 40], iconAnchor: [20, 20] });
    const marker = L.marker([bin.latitude, bin.longitude], { icon });

    marker.bindPopup(`
      <div class="popup-content">
        <div class="popup-content__title">🗑️ ${bin.name}</div>
        <div class="popup-content__row"><span>Remplissage</span><span style="color:${status === 'critical' ? 'var(--red)' : status === 'warning' ? 'var(--amber)' : 'var(--emerald)'}">${bin.fill_level}%</span></div>
        <div class="popup-content__row"><span>Batterie</span><span>${bin.battery}%</span></div>
        <div class="popup-content__row"><span>Température</span><span>${bin.temperature}°C</span></div>
        <div class="popup-content__row"><span>Dernière MAJ</span><span>${formatTime(bin.last_updated)}</span></div>
        ${order ? `<div class="popup-content__row"><span>Ordre collecte</span><span>#${order}</span></div>` : ''}
      </div>
    `, { className: 'dark-popup' });

    marker.addTo(map);
    binMarkers[bin.id] = marker;
  });

  // Garage marker
  if (routeData && routeData.garage) {
    const garageIcon = L.divIcon({
      html: '<div class="garage-marker">🚛</div>',
      className: '', iconSize: [42, 42], iconAnchor: [21, 21],
    });
    L.marker([routeData.garage.latitude, routeData.garage.longitude], { icon: garageIcon })
      .bindPopup('<div class="popup-content"><div class="popup-content__title">🏠 Garage Camion</div><div class="popup-content__row"><span>Point de départ/arrivée</span></div></div>')
      .addTo(map);
  }
}

// ── Render Route ──────────────────────────────────────
function renderRoute(routeData) {
  routeLines.forEach(l => map.removeLayer(l));
  routeLines = [];

  if (!routeData || !routeData.segments) return;

  routeData.segments.forEach((seg, i) => {
    if (!seg.coordinates || seg.coordinates.length < 2) return;

    // Animated ant-path effect via dashed polyline
    const line = L.polyline(seg.coordinates, {
      color: '#10b981',
      weight: 4,
      opacity: 0.8,
      dashArray: '12, 8',
      lineCap: 'round',
    }).addTo(map);

    // Glow layer
    const glow = L.polyline(seg.coordinates, {
      color: '#10b981',
      weight: 8,
      opacity: 0.15,
      lineCap: 'round',
    }).addTo(map);

    routeLines.push(line, glow);
  });
}

// ── Render KPIs ───────────────────────────────────────
function renderKPIs(stats, routeData) {
  document.getElementById('kpi-total').textContent = stats.total_bins;
  document.getElementById('kpi-critical').textContent = stats.critical;
  document.getElementById('kpi-distance').textContent = routeData.total_distance_km + ' km';
  document.getElementById('kpi-co2').textContent = stats.co2_saved_kg + ' kg';

  // Route info in sidebar
  document.getElementById('route-distance').textContent = routeData.total_distance_km + ' km';
  document.getElementById('route-duration').textContent = routeData.total_duration_min + ' min';
  document.getElementById('route-stops').textContent = routeData.ordered_bin_ids.length;
  document.getElementById('route-saved').textContent = stats.distance_saved_km + ' km';
}

// ── Render Bin List ───────────────────────────────────
function renderBinList(bins, routeData) {
  const container = document.getElementById('bin-list');
  const orderMap = {};
  if (routeData && routeData.ordered_bin_ids) {
    routeData.ordered_bin_ids.forEach((id, i) => { orderMap[id] = i + 1; });
  }

  // Sort: critical first, then by fill level desc
  const sorted = [...bins].sort((a, b) => b.fill_level - a.fill_level);

  container.innerHTML = sorted.map(bin => {
    const status = bin.fill_level >= 80 ? 'critical' : bin.fill_level >= 50 ? 'warning' : 'normal';
    const icon = status === 'critical' ? '🔴' : status === 'warning' ? '🟡' : '🟢';
    const order = orderMap[bin.id];
    return `
      <div class="bin-card" onclick="focusBin('${bin.id}')" id="bin-card-${bin.id}">
        <div class="bin-card__icon ${status}">${icon}</div>
        <div class="bin-card__info">
          <div class="bin-card__name">${bin.name}</div>
          <div class="bin-card__meta">
            <span>🔋 ${bin.battery}%</span>
            <span>🌡️ ${bin.temperature}°C</span>
            ${order ? `<span>#${order}</span>` : ''}
          </div>
          <div class="fill-bar"><div class="fill-bar__inner ${status}" style="width:${bin.fill_level}%"></div></div>
        </div>
        <div class="bin-card__fill ${status}">${bin.fill_level}%</div>
      </div>`;
  }).join('');
}

// ── Focus on Bin ──────────────────────────────────────
function focusBin(binId) {
  const bin = binsData.find(b => b.id === binId);
  if (!bin) return;
  map.flyTo([bin.latitude, bin.longitude], 16, { duration: 0.8 });
  if (binMarkers[binId]) binMarkers[binId].openPopup();
  // Highlight card
  document.querySelectorAll('.bin-card').forEach(c => c.classList.remove('active'));
  const card = document.getElementById(`bin-card-${binId}`);
  if (card) card.classList.add('active');
}

// ── Charts ────────────────────────────────────────────
async function loadChartData() {
  try {
    const res = await fetch(`${API_BASE}/api/bins/history?hours=24`);
    const history = await res.json();
    renderChart(history);
  } catch (err) {
    console.error('Chart load error:', err);
  }
}

function renderChart(history) {
  const ctx = document.getElementById('main-chart');
  if (!ctx) return;

  if (chartInstance) chartInstance.destroy();

  if (currentChartTab === 'trend') {
    renderTrendChart(ctx, history);
  } else if (currentChartTab === 'distribution') {
    renderDistributionChart(ctx);
  } else {
    renderEfficiencyChart(ctx);
  }
}

function renderTrendChart(ctx, history) {
  // Group by bin
  const binGroups = {};
  history.forEach(h => {
    if (!binGroups[h.bin_name]) binGroups[h.bin_name] = [];
    binGroups[h.bin_name].push(h);
  });

  const colors = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];
  const datasets = Object.entries(binGroups).map(([name, data], i) => ({
    label: name,
    data: data.map(d => ({ x: new Date(d.timestamp), y: d.fill_level })),
    borderColor: colors[i % colors.length],
    backgroundColor: colors[i % colors.length] + '20',
    borderWidth: 2,
    pointRadius: 0,
    tension: 0.4,
    fill: true,
  }));

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          time: { unit: 'hour', displayFormats: { hour: 'HH:mm' } },
          grid: { color: 'rgba(56,96,160,0.1)' },
          ticks: { color: '#56678a', font: { size: 10 } },
        },
        y: {
          min: 0, max: 100,
          grid: { color: 'rgba(56,96,160,0.1)' },
          ticks: { color: '#56678a', font: { size: 10 }, callback: v => v + '%' },
        },
      },
      plugins: {
        legend: { display: true, position: 'bottom', labels: { color: '#8899b8', font: { size: 10 }, boxWidth: 12, padding: 8 } },
        tooltip: { backgroundColor: 'rgba(13,21,46,0.95)', titleColor: '#e8edf5', bodyColor: '#8899b8', borderColor: 'rgba(56,96,160,0.3)', borderWidth: 1 },
      },
    },
  });
}

function renderDistributionChart(ctx) {
  const normal = binsData.filter(b => b.fill_level < 50).length;
  const warning = binsData.filter(b => b.fill_level >= 50 && b.fill_level < 80).length;
  const critical = binsData.filter(b => b.fill_level >= 80).length;

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Normal (<50%)', 'Attention (50-80%)', 'Critique (>80%)'],
      datasets: [{
        data: [normal, warning, critical],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: '#0a1128',
        borderWidth: 3,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { color: '#8899b8', font: { size: 10 }, padding: 12 } },
      },
    },
  });
}

function renderEfficiencyChart(ctx) {
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: binsData.map(b => b.name.replace('Bin ', '')),
      datasets: [{
        label: 'Remplissage (%)',
        data: binsData.map(b => b.fill_level),
        backgroundColor: binsData.map(b =>
          b.fill_level >= 80 ? '#ef4444' : b.fill_level >= 50 ? '#f59e0b' : '#10b981'
        ),
        borderRadius: 6,
        barThickness: 28,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: { max: 100, grid: { color: 'rgba(56,96,160,0.1)' }, ticks: { color: '#56678a', callback: v => v + '%' } },
        y: { grid: { display: false }, ticks: { color: '#8899b8', font: { size: 10 } } },
      },
      plugins: { legend: { display: false } },
    },
  });
}

// ── Event Listeners ───────────────────────────────────
function setupEventListeners() {
  // Strategy toggle
  document.querySelectorAll('.strategy-toggle__btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.strategy-toggle__btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentStrategy = btn.dataset.strategy;
      loadDashboard();
    });
  });

  // Chart tabs
  document.querySelectorAll('.chart-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentChartTab = tab.dataset.tab;
      loadChartData();
    });
  });

  // Charts panel toggle
  document.getElementById('charts-toggle')?.addEventListener('click', () => {
    document.querySelector('.charts-panel').classList.toggle('collapsed');
    chartsCollapsed = !chartsCollapsed;
    document.getElementById('charts-toggle').textContent = chartsCollapsed ? '▲' : '▼';
  });

  // Fill level slider
  const slider = document.getElementById('fill-slider');
  const sliderVal = document.getElementById('slider-value');
  if (slider && sliderVal) {
    slider.addEventListener('input', () => {
      sliderVal.textContent = slider.value + '%';
      updateSliderColor(slider);
    });
  }

  // Update form
  document.getElementById('update-form')?.addEventListener('submit', handleUpdate);
}

function updateSliderColor(slider) {
  const val = parseInt(slider.value);
  const color = val >= 80 ? '#ef4444' : val >= 50 ? '#f59e0b' : '#10b981';
  slider.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${val}%, #0a1128 ${val}%, #0a1128 100%)`;
}

// ── Bin Update ────────────────────────────────────────
async function handleUpdate(e) {
  e.preventDefault();
  const binId = document.getElementById('bin-select').value;
  const fill = document.getElementById('fill-slider').value;
  const log = document.getElementById('update-log');

  try {
    const res = await fetch(`${API_BASE}/api/bins/${binId}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fill_level: parseInt(fill) }),
    });
    if (!res.ok) throw new Error('Update failed');
    log.className = 'update-log success';
    log.textContent = `✅ Bin ${binId} mis à jour à ${fill}%`;
    loadDashboard();
  } catch (err) {
    log.className = 'update-log error';
    log.textContent = '❌ Erreur de mise à jour';
  }
}

// ── Helpers ───────────────────────────────────────────
function formatTime(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  const now = new Date();
  const diff = Math.round((now - d) / 60000);
  if (diff < 1) return 'à l\'instant';
  if (diff < 60) return `il y a ${diff} min`;
  return `il y a ${Math.floor(diff / 60)}h`;
}
