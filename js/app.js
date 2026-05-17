(function () {
  'use strict';

  const API = '/api';
  let token = localStorage.getItem('klinos_token') || '';
  let currentUser = null;
  let currentPatientId = null;

  // ─── Auth helpers ───
  function getHeaders() {
    const h = { 'Content-Type': 'application/json' };
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }

  async function api(path, options) {
    const res = await fetch(API + path, {
      headers: getHeaders(),
      ...options,
    });
    if (!res.ok) {
      const text = await res.text();
      if (res.status === 401) { logout(); }
      throw new Error(text);
    }
    return res.json();
  }

  const get = (path) => api(path);
  const post = (path, data) => api(path, { method: 'POST', body: JSON.stringify(data) });
  const put = (path, data) => api(path, { method: 'PUT', body: JSON.stringify(data) });
  const del = (path) => api(path, { method: 'DELETE' });

  // ─── Login ───
  window.login = async function () {
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value.trim();
    const errEl = document.getElementById('login-error');
    try {
      const res = await fetch(API + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) { errEl.style.display = 'block'; return; }
      const data = await res.json();
      token = data.token;
      currentUser = data.user;
      localStorage.setItem('klinos_token', token);
      localStorage.setItem('klinos_user', JSON.stringify(currentUser));
      document.getElementById('login-overlay').classList.add('hidden');
      applyPermissions(currentUser.permissions);
      updateSidebarUser(currentUser);
      loadDashboard();
      loadPacientesList();
      loadConfig();
      applyDarkMode();
      applyThemeColor();
    } catch (e) {
      errEl.style.display = 'block';
    }
  };

  window.logout = function () {
    if (token) {
      fetch(API + '/auth/logout', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
      }).catch(() => {});
    }
    token = '';
    currentUser = null;
    localStorage.removeItem('klinos_token');
    localStorage.removeItem('klinos_user');
    location.reload();
  };

  function updateSidebarUser(user) {
    const name = user.nombre;
    const initials = name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    document.getElementById('sb-avatar').textContent = initials;
    document.getElementById('sb-name').textContent = name;
    document.getElementById('sb-role').textContent = user.rol;
  }

  // ─── Permissions & Navigation ───
  // navId (from onclick) -> panel ID
  const panelMap = {
    dashboard: 'p-dashboard', agenda: 'p-agenda', reservar: 'p-reservar',
    pacientes: 'p-pacientes', historial: 'p-historial', sesiones: 'p-sesiones',
    klinos: 'p-klinos',
    carga: 'p-carga', terapeutas: 'p-terapeutas', eventos: 'p-eventos',
    cursos: 'p-cursos', miembros: 'p-miembros', finanzas: 'p-finanzas',
    terapias: 'p-terapias',
    configuracion: 'p-configuracion',
  };
  // navId -> permission key in DB
  const permMap = {
    dashboard: 'dashboard', agenda: 'agenda', reservar: 'reservar',
    pacientes: 'pacientes', terapeutas: 'terapeutas',
    citas: 'citas', finanzas: 'finanzas',
    eventos: 'eventos', cursos: 'cursos', miembros: 'miembros',
    sesiones: 'klinos', klinos: 'klinos', configuracion: 'config',
    historial: 'historial', carga: 'carga', terapias: 'config',
  };

  function applyPermissions(permsStr) {
    let perms;
    try { perms = JSON.parse(permsStr); } catch (e) { perms = {}; }
    // Set dataset on panels
    for (const [navId, panelId] of Object.entries(panelMap)) {
      const pk = permMap[navId] || navId;
      const perm = perms[pk] || 'hide';
      const panel = document.getElementById(panelId);
      if (panel) panel.dataset.perm = perm;
    }
    // Show/hide nav items
    for (const [navId] of Object.entries(panelMap)) {
      const pk = permMap[navId] || navId;
      const perm = perms[pk] || 'hide';
      const navEl = document.querySelector(`[onclick*="nav('${navId}'"]`) || document.querySelector(`[onclick*='nav("${navId}"']`);
      if (navEl) {
        if (perm === 'hide') navEl.classList.add('sb-hide');
        else navEl.classList.remove('sb-hide');
      }
    }
  }

  function canView(navId) {
    const pk = permMap[navId] || navId;
    const panel = document.getElementById(panelMap[navId]);
    if (!panel) return true;
    const perm = panel.dataset.perm || 'hide';
    return perm !== 'hide';
  }

  // ─── Navigation ───
  const views = {
    dashboard: 'Dashboard', agenda: 'Agenda', reservar: 'Reservar Hora',
    pacientes: 'Pacientes', historial: 'Historial de Citas',
    sesiones: 'Sesiones · Klinós',
    klinos: 'Memoria Clínica · Klinós', carga: 'Carga Emocional del Terapeuta',
    terapeutas: 'Terapeutas', eventos: 'Eventos', cursos: 'Cursos',
    miembros: 'Miembros', finanzas: 'Finanzas', terapias: 'Terapias',
    configuracion: 'Configuración',
  };

  window.nav = function (id, el) {
    if (!canView(id)) return;
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.sb-item').forEach(s => s.classList.remove('active'));
    const p = document.getElementById('p-' + id);
    if (p) p.classList.add('active');
    if (el) el.classList.add('active');
    document.getElementById('topbar-title').textContent = views[id] || id;
    if (id === 'pacientes') { hideDetail(); loadPacientesList(); }
    if (id === 'dashboard') loadDashboard();
    if (id === 'agenda') loadAgenda();
    if (id === 'sesiones') loadSesiones();
    if (id === 'historial') loadHistorial();
    if (id === 'klinos') loadKlinos();
    if (id === 'carga') loadCarga();
    if (id === 'terapeutas') loadTerapeutas();
    if (id === 'eventos') loadEventos();
    if (id === 'cursos') loadCursos();
    if (id === 'miembros') loadMiembros();
    if (id === 'finanzas') loadFinanzas();
    if (id === 'terapias') loadTerapias();
    if (id === 'configuracion') { loadConfig(); applyDarkMode(); applyThemeColor(); applyFontSize(); loadUsers(); }
    if (id === 'reservar') loadTipoSesionOptions();
  };

  // ─── Utilities ───
  function initials(name) {
    return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  }

  const avatarColors = ['av-l-sage', 'av-l-blue', 'av-l-amber', 'av-l-rose', 'av-l-purple'];
  const avatarSolid = { blue: 'av-blue', sage: 'av-sage', rose: 'av-rose', amber: 'av-amber' };

  function avatarClass(color) { return avatarSolid[color] || 'av-l-sage'; }

  function statusBadge(estado) {
    const map = {
      confirmada: 'badge-green',
      pendiente_pago: 'badge-amber',
      completada: 'badge-blue',
      cancelada: 'badge-rose',
      Pagado: 'paid',
      Pendiente: 'pend',
    };
    const cls = map[estado] || 'badge-gray';
    const label = estado.replace(/_/g, ' ');
    return `<span class="badge ${cls}">${label}</span>`;
  }

  function applyDarkMode() {
    const saved = localStorage.getItem('klinos_dark') === 'true';
    const toggle = document.getElementById('dark-toggle');
    if (saved) {
      document.documentElement.classList.add('dark');
      if (toggle) toggle.classList.add('active');
    } else {
      document.documentElement.classList.remove('dark');
      if (toggle) toggle.classList.remove('active');
    }
  }

  window.toggleDark = function () {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('klinos_dark', isDark);
    const toggle = document.getElementById('dark-toggle');
    if (toggle) toggle.classList.toggle('active', isDark);
  };

  // ─── Patient detail state ───
  window.showDetail = function (id) {
    if (!canView('pacientes')) return;
    const num = parseInt(id.replace('p', ''));
    currentPatientId = num;
    document.getElementById('pac-list').style.display = 'none';
    const d = document.getElementById('pac-detail');
    d.style.display = 'flex';
    d.innerHTML = '<div class="loading"><div class="spinner"></div>Cargando paciente...</div>';
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('p-pacientes').classList.add('active');
    document.querySelectorAll('.sb-item').forEach(s => s.classList.remove('active'));
    const pacNav = document.querySelector('.sb-item[onclick*="pacientes"]');
    if (pacNav) pacNav.classList.add('active');
    document.getElementById('topbar-title').textContent = views.pacientes;
    loadPacienteDetail(num);
  };

  function hideDetail() {
    currentPatientId = null;
    document.getElementById('pac-list').style.display = 'block';
    document.getElementById('pac-detail').style.display = 'none';
  }
  window.hideDetail = hideDetail;

  // ─── Load: Dashboard ───
  async function loadDashboard() {
    try {
      const stats = await get('/dashboard/stats');
      const el = document.getElementById('dashboard-stats');
      if (el) {
        el.querySelector('[data-stat="citas"]').textContent = stats.citas_hoy;
        el.querySelector('[data-stat="pacientes"]').textContent = stats.pacientes_activos;
        el.querySelector('[data-stat="pagos"]').textContent = stats.pagos_pendientes;
        el.querySelector('[data-stat="terapeutas"]').textContent = stats.terapeutas_activos;
      }
    } catch (e) { console.error('Dashboard load error', e); }

    loadCitasHoy();
    loadTerapeutasGrid();
    loadProximoSesion();
  }

  async function loadCitasHoy() {
    try {
      const citas = await get('/citas?fecha=15%20abr');
      const el = document.getElementById('citas-hoy');
      if (!el) return;
      if (citas.length === 0) { el.innerHTML = '<div class="list-item"><div class="list-info"><div class="list-name">Sin citas para hoy</div></div></div>'; return; }
      el.innerHTML = citas.map(c => `
        <div class="list-item">
          <div class="list-time">${c.hora}</div>
          <div class="av av-sm ${avatarColors[c.paciente_id % avatarColors.length]}">${initials(c.paciente?.nombre || '??')}</div>
          <div class="list-info">
            <div class="list-name">${c.paciente?.nombre || 'Paciente'}</div>
            <div class="list-sub">${c.tipo_sesion} · ${c.terapeuta?.nombre || ''} · ${c.sala} · ${c.duracion} min</div>
          </div>
          ${statusBadge(c.estado)}
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  async function loadTerapeutasGrid() {
    try {
      const terapeutas = await get('/terapeutas');
      const el = document.getElementById('terapeutas-grid');
      if (!el) return;
      if (terapeutas.length === 0) return;
      const colors = ['av-blue', 'av-rose', 'av-sage', 'av-amber'];
      el.innerHTML = terapeutas.map((t, i) => `
        <div class="card card-pad flex-center gap-12">
          <div class="av av-sm ${colors[i % colors.length]}">${initials(t.nombre)}</div>
          <div class="flex-1"><div class="fs-12 fw-500">${t.nombre}</div><div class="fs-11 text-3">${t.especialidad}</div></div>
          <span class="badge badge-blue">${t.citas?.length || 0} cita${t.citas?.length !== 1 ? 's' : ''}</span>
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  async function loadProximoSesion() {
    try {
      const citas = await get('/citas?fecha=15%20abr');
      if (citas.length === 0) return;
      const next = citas[0];
      const el = document.getElementById('countdown-next');
      if (!el) return;
      el.innerHTML = `
        <div class="fs-10 fw-500" style="text-transform:uppercase;letter-spacing:0.5px;color:var(--green)">Próxima sesión</div>
        <div class="lora fs-15 mt-3" style="color:var(--text)">${next.paciente?.nombre || 'Paciente'} — ${next.tipo_sesion}</div>
        <div class="fs-11 mt-3" style="color:var(--green)">En breve · ${next.hora} · ${next.sala} · ${next.terapeuta?.nombre || ''}</div>
      `;
    } catch (e) { console.error(e); }
  }

  // ─── Load: Pacientes list ───
  async function loadPacientesList() {
    try {
      const pacientes = await get('/pacientes');
      const el = document.getElementById('pacientes-grid');
      if (!el) return;
      document.getElementById('pacientes-count').textContent = `${pacientes.length} pacientes activos · 0 archivados`;
      el.innerHTML = pacientes.map((p, i) => `
        <div class="p-card" onclick="showDetail('p${p.id}')">
          <div class="flex-center gap-10 mb-10">
            <div class="av av-sm ${avatarColors[i % avatarColors.length]}">${initials(p.nombre)}</div>
            <div><div class="fs-13 fw-500">${p.nombre}</div><div class="fs-10 text-3">${p.sesiones_total} sesiones · Últ: ${p.ultima_sesion || '—'}</div></div>
          </div>
          <div class="flex-between">
            <span class="p-status ${statusClass(p.status)}">${p.status}</span>
            <span class="fs-10 text-3">${p.rut}</span>
          </div>
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  function statusClass(s) {
    const map = { 'Trabajo activo': 's-work', 'Exploración': 's-exp', 'En cierre': 's-close', 'Archivado': 's-pause' };
    return map[s] || 's-work';
  }

  // ─── Load: Paciente detail ───
  async function loadPacienteDetail(id) {
    try {
      const [p, notas, patrones, preparaciones, historial] = await Promise.all([
        get('/pacientes/' + id),
        get('/klinos/notas/' + id),
        get('/klinos/patrones/' + id),
        get('/klinos/preparaciones/' + id),
        get('/klinos/historial/' + id),
      ]);

      const el = document.getElementById('pac-detail');
      el.innerHTML = `
        <button class="back-btn" onclick="hideDetail()">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 12L6 8l4-4"/></svg>
          Volver a pacientes
        </button>

        <div class="card card-pad flex-center gap-16">
          <div class="av av-lg ${avatarColors[p.id % avatarColors.length]}">${initials(p.nombre)}</div>
          <div class="flex-1">
            <div class="lora fs-18">${p.nombre}</div>
            <div class="fs-11 text-3 mt-3">${p.rut || '—'} · ${p.edad} años · Inicio: ${p.fecha_inicio || '—'} · ${p.email || '—'} · ${p.telefono || '—'}</div>
            <div class="mt-8 flex gap-6 flex-wrap">
              <span class="badge ${p.status === 'Trabajo activo' ? 'badge-green' : 'badge-gray'}">${p.status}</span>
              ${p.diagnostico ? `<span class="badge badge-blue">${p.diagnostico}</span>` : ''}
            </div>
          </div>
          <div class="text-right flex-shrink-0">
            <div class="fs-28 lora lh-1">${p.sesiones_total}</div>
            <div class="fs-10 text-3">sesiones</div>
            <div class="mt-6 flex gap-5 justify-end">
              <button class="btn-outline btn-sm">Archivar</button>
              <button class="btn-primary btn-sm" onclick="nav('reservar',document.querySelector('[onclick*=reservar]'))">+ Sesión</button>
            </div>
          </div>
        </div>

        <div class="alert alert-sage">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 12V5a2 2 0 012-2h8a2 2 0 012 2v7"/><path d="M1 12h14M6 8h4M6 10.5h2"/></svg>
          <span><strong>Klinós detectó:</strong> ${patrones.length > 0 ? `El tema "${patrones[0].patron}" aparece en ${patrones[0].frecuencia} sesiones.` : 'Sin patrones detectados todavía.'}</span>
        </div>

        <div class="grid-2">
          <div class="card card-pad">
            <div class="card-title">Patrones detectados por Klinós</div>
            ${patrones.length > 0 ? patrones.map(pat => `<span class="chip">${pat.patron} (x${pat.frecuencia})</span>`).join('') : '<div class="fs-11 text-3">Sin patrones aún</div>'}
            <div class="fs-10 text-3 mt-8">Basado en notas libres de las últimas sesiones</div>
          </div>

          <div class="card card-pad">
            <div class="card-title">Preparación — próxima sesión</div>
            ${preparaciones.length > 0 ? preparaciones.map(prep => `
              <div class="check-row" onclick="togglePrep(${prep.id})" style="cursor:pointer">
                <div class="check-box ${prep.completado ? 'check-done' : ''}">${prep.completado ? '<svg width="9" height="9" viewBox="0 0 9 9"><path d="M1.5 4.5l2 2L7.5 2" stroke="#fff" stroke-width="1.5" stroke-linecap="round" fill="none"/></svg>' : ''}</div>
                ${prep.item}
              </div>
            `).join('') : '<div class="fs-11 text-3">Sin items pendientes</div>'}
          </div>
        </div>

        <div class="card card-pad">
          <div class="card-title">Progreso del proceso terapéutico</div>
          <div class="flex-between fs-10 text-3 mb-3"><span>Exploración</span><span>Trabajo activo</span><span>Consolidación</span><span>Cierre</span></div>
          <div class="progress-track"><div class="progress-fill" style="width:${Math.min(p.sesiones_total * 5, 95)}%"></div></div>
          <div class="flex-between mt-8">
            <span class="fs-11 text-3">Sesión ${p.sesiones_total} de proceso estimado</span>
            <span class="badge badge-green">Sin estancamiento</span>
          </div>
        </div>

        <div class="card card-pad">
          <div class="card-title">Historial de sesiones</div>
          ${historial.length > 0 ? historial.map(h => `
            <div class="t-line"><div class="t-dot"></div><span class="t-date">${h.fecha}</span><span class="text-2">${h.contenido}</span></div>
          `).join('') : '<div class="fs-11 text-3">Sin historial</div>'}
        </div>

        <div class="card card-pad">
          <div class="card-title">Notas clínicas libres</div>
          <textarea id="nota-textarea" class="w-full" rows="4" placeholder="Escribe notas libremente. Klinós organizará la información automáticamente...">${notas.length > 0 ? notas[0].contenido : ''}</textarea>
          <div class="flex gap-8 justify-end mt-10">
            <button class="btn-outline btn-sm" onclick="document.getElementById('nota-textarea').value = ''">Cancelar</button>
            <button class="btn-primary btn-sm" onclick="saveNota(${p.id})">Guardar notas</button>
          </div>
        </div>
      `;
    } catch (e) { console.error(e); }
  }

  // ─── Notas ───
  window.saveNota = async function (pacienteId) {
    const contenido = document.getElementById('nota-textarea').value;
    await post('/klinos/notas', { paciente_id: pacienteId, contenido });
    showToast('Notas guardadas', 'success');
  };

  // ─── Toggle preparación ───
  window.togglePrep = async function (id) {
    await put('/klinos/preparaciones/' + id);
    if (currentPatientId) loadPacienteDetail(currentPatientId);
  };

  // ─── Load: Agenda ───
  async function loadAgenda() {
    try {
      const citas = await get('/citas?fecha=15%20abr');
      const terapeutas = await get('/terapeutas');

      const horas = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '14:00', '15:00', '16:00'];
      const grid = document.querySelector('.agenda-grid');
      if (!grid) return;

      const headerRow = grid.querySelector('.ag-header');
      grid.innerHTML = '';
      if (headerRow) {
        headerRow.style.gridTemplateColumns = `64px repeat(${terapeutas.length}, 1fr)`;
        grid.appendChild(headerRow);
      }

      const agColors = { confirmada: 'ag-confirmada', pendiente_pago: 'ag-pendiente_pago', completada: 'ag-completada', cancelada: 'ag-cancelada' };

      horas.forEach(hora => {
        const row = document.createElement('div');
        row.className = 'ag-row';
        row.style.gridTemplateColumns = `64px repeat(${terapeutas.length}, 1fr)`;
        row.innerHTML = `<div class="ag-time">${hora}</div>`;
        terapeutas.forEach(t => {
          const cita = citas.find(c => c.hora === hora && c.terapeuta_id === t.id);
          if (cita) {
            const colorCls = agColors[cita.estado] || 'ag-confirmada';
            row.innerHTML += `
              <div class="ag-cell"><div class="ag-appt ${colorCls}"><strong>${cita.paciente?.nombre || ''}</strong>${cita.tipo_sesion} · ${cita.duracion}m</div></div>
            `;
          } else {
            row.innerHTML += '<div class="ag-cell"></div>';
          }
        });
        grid.appendChild(row);
      });
    } catch (e) { console.error(e); }
  }

  // ─── Load: Historial ───
  async function loadHistorial() {
    try {
      const citas = await get('/citas');
      const el = document.getElementById('historial-list');
      if (!el) return;
      el.innerHTML = citas.map(c => `
        <div class="list-item">
          <div class="min-w-86 fs-11 text-3">${c.fecha} · ${c.hora}</div>
          <div class="av av-xs ${avatarColors[c.paciente_id % avatarColors.length]} flex-shrink-0">${initials(c.paciente?.nombre || '??')}</div>
          <div class="list-info">
            <div class="list-name">${c.paciente?.nombre || 'Paciente'}</div>
            <div class="list-sub">${c.tipo_sesion} · ${c.terapeuta?.nombre || ''} · ${c.duracion} min</div>
          </div>
          ${statusBadge(c.estado)}
        </div>
      `).join('');
      document.getElementById('historial-count').textContent = `${citas.length} citas en total`;
    } catch (e) { console.error(e); }
  }

  // ─── Load: Klinós ───
  async function loadKlinos() {
    try {
      const pacientes = await get('/pacientes');
      const el = document.getElementById('klinos-list');
      if (el) {
      el.innerHTML = pacientes.map((p, i) => {
        const pct = Math.min(p.sesiones_total * 5, 95);
        const statusLabel = p.sesiones_total > 10 ? 'Buen progreso' : p.sesiones_total > 5 ? 'En evolución' : 'Fase inicial';
        const statusBadgeCls = p.sesiones_total > 10 ? 'badge-green' : p.sesiones_total > 5 ? 'badge-amber' : 'badge-gray';
        return `
          <div class="card card-pad cursor-pointer" onclick="showDetail('p${p.id}');nav('pacientes',document.querySelector('[onclick*=pacientes]'))">
            <div class="flex-center gap-12">
              <div class="av av-sm ${avatarColors[i % avatarColors.length]}">${initials(p.nombre)}</div>
              <div class="flex-1"><div class="fs-13 fw-500">${p.nombre}</div><div class="fs-11 text-3">${p.diagnostico || ''} · ${p.terapeuta?.nombre || ''} · Sesión ${p.sesiones_total}</div></div>
              <div class="text-right flex-shrink-0"><span class="badge ${statusBadgeCls}">${statusLabel}</span></div>
            </div>
            <div class="progress-track mt-8"><div class="progress-fill" style="width:${pct}%"></div></div>
          </div>
        `;
      }).join('');
      }
      // Populate chat paciente selector
      const select = document.getElementById('chat-paciente');
      if (select) {
        select.innerHTML = '<option value="0">Sin contexto de paciente</option>' +
          pacientes.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('');
      }
    } catch (e) { console.error(e); }
  }

  // ─── Load: Carga Emocional ───
  async function loadCarga() {
    try {
      const citas = await get('/citas?fecha=15%20abr');
      const total = citas.length;
      const altaEl = document.querySelector('[data-carga="alta"]');
      const sesEl = document.querySelector('[data-carga="sesiones"]');
      if (sesEl) sesEl.textContent = total;
      if (altaEl) altaEl.textContent = Math.ceil(total * 0.5);
    } catch (e) { console.error(e); }
  }

  // ─── Load: Terapeutas ───
  async function loadTerapeutas() {
    try {
      const terapeutas = await get('/terapeutas');
      const el = document.getElementById('terapeutas-list');
      if (!el) return;
      const solidColors = ['av-blue', 'av-sage', 'av-rose', 'av-amber'];
      el.innerHTML = terapeutas.map((t, i) => `
        <div class="card card-pad">
          <div class="flex-center gap-12 mb-10">
            <div class="av av-md ${solidColors[i % solidColors.length]}">${initials(t.nombre)}</div>
            <div><div class="fs-14 fw-500">${t.nombre}</div><div class="fs-11 text-3">${t.especialidad}</div></div>
          </div>
          <div class="fs-11 text-2 lh-18">
            <div>📧 ${t.email}</div>
            <div>📱 ${t.telefono}</div>
            <div>📅 ${t.horario}</div>
          </div>
          <div class="mt-8 fs-11 text-3">Especialidades: ${t.especialidad}</div>
          <div class="flex gap-6 mt-10"><button class="btn-outline btn-sm">Editar</button><button class="btn-danger btn-sm">Eliminar</button></div>
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  // ─── Load: Eventos ───
  async function loadEventos() {
    try {
      const eventos = await get('/eventos');
      const el = document.getElementById('eventos-list');
      if (!el) return;
      el.innerHTML = eventos.map(e => `
        <div class="ev-card">
          <div class="lora fs-14">${e.nombre}</div>
          <div class="fs-11 text-3">${e.descripcion}</div>
          <div class="ev-chip"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="2" width="14" height="13" rx="1.5"/><path d="M1 6h14"/></svg>${e.fecha_inicio} – ${e.fecha_fin}</div>
          <div class="ev-chip"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 2C5.2 2 3 4.2 3 7c0 4.5 5 9 5 9s5-4.5 5-9c0-2.8-2.2-5-5-5z"/></svg>${e.ubicacion}</div>
          <div class="flex gap-12 fs-11 text-3"><span>${e.terapeutas_count} terapeutas</span><span>${e.citas_count} citas registradas</span></div>
          <button class="btn-outline btn-sm self-start">Gestionar →</button>
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  // ─── Load: Cursos ───
  async function loadCursos() {
    try {
      const cursos = await get('/cursos');
      const el = document.getElementById('cursos-list');
      if (!el) return;
      const tagColors = { Mensual: 'var(--green-light)', 'Pago único': 'var(--blue-light)' };
      const tagTextColors = { Mensual: 'var(--green)', 'Pago único': 'var(--blue)' };
      el.innerHTML = cursos.map(c => `
        <div class="course-card">
          <div class="flex-between" style="align-items:flex-start;margin-bottom:8px">
            <div class="lora fs-14">${c.nombre}</div>
            <span class="course-tag" style="background:${tagColors[c.tipo_pago] || 'var(--green-light)'};color:${tagTextColors[c.tipo_pago] || 'var(--green)'}">${c.tag}</span>
          </div>
          <div class="fs-11 text-3 lh-18">
            <div><strong class="text-2">Tipo:</strong> ${c.tipo}</div>
            <div><strong class="text-2">Profesor:</strong> ${c.profesor}</div>
            <div><strong class="text-2">Horario:</strong> ${c.horario}</div>
            <div><strong class="text-2">Monto:</strong> ${c.monto}</div>
            <div><strong class="text-2">Inscritos:</strong> ${c.alumnos} alumnos</div>
          </div>
          <div class="flex gap-6 mt-10">
            <button class="btn-outline btn-sm flex-1">Ver detalle</button>
            <button class="btn-danger btn-sm">Eliminar</button>
          </div>
        </div>
      `).join('');
    } catch (e) { console.error(e); }
  }

  // ─── Load: Miembros ───
  async function loadMiembros() {
    try {
      const miembros = await get('/miembros');
      const el = document.getElementById('miembros-table-body');
      if (!el) return;
      const roleColors = { Admin: 'badge-blue', Terapeuta: 'badge-green', Recepción: 'badge-amber' };
      el.innerHTML = miembros.map(m => `
        <tr>
          <td><div class="flex-center gap-8"><div class="av av-xs ${avatarClass(m.avatar_color)}">${initials(m.nombre)}</div>${m.nombre}</div></td>
          <td>${m.email}</td>
          <td><span class="badge ${roleColors[m.rol] || 'badge-gray'}">${m.rol}</span></td>
          <td class="text-3">${m.fecha_ingreso}</td>
          <td><button class="btn-danger btn-sm" onclick="removeMember(${m.id})">Eliminar</button></td>
        </tr>
      `).join('');
    } catch (e) { console.error(e); }
  }

  window.removeMember = async function (id) {
    if (!confirm('¿Eliminar miembro?')) return;
    await del('/miembros/' + id);
    loadMiembros();
  };

  // ─── Load: Finanzas ───
  async function loadFinanzas() {
    try {
      const finanzas = await get('/finanzas');
      const el = document.getElementById('finanzas-table-body');
      if (!el) return;
      el.innerHTML = finanzas.map(f => `
        <tr>
          <td>${f.paciente}</td>
          <td>${f.terapeuta}</td>
          <td>${f.tipo}</td>
          <td>${f.fecha}</td>
          <td>$${f.monto.toLocaleString('es-CL')}</td>
          <td class="${f.estado === 'Pagado' ? 'paid' : 'pend'}">${f.estado}</td>
        </tr>
      `).join('');
    } catch (e) { console.error(e); }
  }

  // ─── Toast ───
  function showToast(msg, type) {
    let toast = document.querySelector('.toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.className = 'toast toast-' + type + ' show';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), 2500);
  }

  // ─── Sesiones ───
  let sesionActualId = null;

  async function loadSesiones() {
    document.getElementById('sesion-writing').style.display = 'none';
    document.getElementById('sesion-analisis').style.display = 'none';
    document.getElementById('sesiones-grid').style.display = 'grid';
    try {
      let sesiones = [];
      const user = currentUser;
      if (user && user.rol === 'admin') {
        // Admin sees all terapeutas' sessions
        const terapeutas = await get('/terapeutas');
        for (const t of terapeutas) {
          const ss = await get('/klinos/sesiones/terapeuta/' + t.id);
          sesiones = sesiones.concat(ss);
        }
      } else if (user && user.rol === 'terapeuta') {
        const nombre = user.nombre;
        sesiones = await get('/klinos/sesiones/terapeuta/by-name/' + encodeURIComponent(nombre));
        // If no results, try searching by common name
        if (sesiones.length === 0) {
          const simple = nombre.split(' ')[0];
          sesiones = await get('/klinos/sesiones/terapeuta/by-name/' + encodeURIComponent(simple));
        }
      } else {
        const terapeutas = await get('/terapeutas');
        for (const t of terapeutas) {
          const ss = await get('/klinos/sesiones/terapeuta/' + t.id);
          sesiones = sesiones.concat(ss);
        }
      }
      document.getElementById('sesiones-count').textContent = sesiones.length + ' sesiones';
      const grid = document.getElementById('sesiones-grid');
      // Group by hour
      const grouped = {};
      sesiones.forEach(s => {
        const key = s.hora || 'sin hora';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(s);
      });
      grid.innerHTML = Object.keys(grouped).sort().map(hora => {
        const cards = grouped[hora].map(s => {
          const estadoCls = s.sesion_estado === 'activa' ? 'activa' : s.sesion_estado === 'cerrada' ? 'cerrada' : '';
          const intensidadMap2 = { baja: 'baja', media: 'media', alta: 'alta' };
          const intensidadCls = intensidadMap2[s.intensidad] || '';
          const badge = s.sesion_estado === 'cerrada'
            ? '<span class="ses-intensidad ' + intensidadCls + '">' + (s.intensidad || '—') + '</span>'
            : s.sesion_estado === 'activa'
              ? '<span class="badge badge-amber">En sesión</span>'
              : '<span class="badge badge-gray">Pendiente</span>';
          const analisis = s.sesion_estado === 'cerrada' && s.analisis
            ? '<div class="fs-11 text-3 mt-6">' + s.analisis.substring(0, 100) + (s.analisis.length > 100 ? '...' : '') + '</div>'
            : '';
          return '<div class="ses-card ' + estadoCls + '" onclick="abrirSesion(' + s.id + ', ' + (s.registro_id || 'null') + ', \'' + s.sesion_estado + '\')">'
            + '<div class="flex-center gap-10">'
            + '<div class="ses-hora">' + s.hora + '</div>'
            + '<div class="flex-1 min-w-0">'
            + '<div class="fs-13 fw-500">' + s.paciente + '</div>'
            + '<div class="fs-11 text-3">' + s.tipo_sesion + ' · ' + s.sala + '</div>'
            + '</div>'
            + badge
            + '</div>'
            + analisis
            + '</div>';
        }).join('');
        return '<div class="sec-lbl mt-8 mb-3" style="grid-column:1/-1">' + hora + '</div>' + cards;
      }).join('');
    } catch (e) { console.error(e); }
  }

  window.abrirSesion = function (citaId, registroId, estado) {
    if (estado === 'cerrada') return;
    document.getElementById('sesiones-grid').style.display = 'none';
    document.getElementById('sesion-writing').style.display = 'flex';
    document.getElementById('sw-paciente').textContent = 'Cargando...';
    document.getElementById('sw-info').textContent = '';
    document.getElementById('sw-notas').value = '';
    document.getElementById('btn-cerrar-sesion').dataset.registroId = '';
    const swInfo = document.getElementById('sw-paciente-info');
    if (swInfo) swInfo.style.display = 'none';
    const swPrev = document.getElementById('sw-sesiones-previas');
    if (swPrev) { swPrev.style.display = 'none'; swPrev.innerHTML = ''; }
    sesionActualId = null;

    // Fetch cita info to get paciente_id and details
    get('/citas/' + citaId).then(cita => {
      document.getElementById('sw-paciente').textContent = cita.paciente?.nombre || 'Paciente';
      document.getElementById('sw-info').textContent = cita.tipo_sesion + ' · ' + cita.sala + ' · ' + cita.hora;
      const pacienteId = cita.paciente_id;
      if (pacienteId) {
        Promise.all([
          get('/pacientes/' + pacienteId),
          get('/klinos/patrones/' + pacienteId),
          get('/klinos/historial/' + pacienteId),
          get('/klinos/sesiones/terapeuta/' + cita.terapeuta_id),
          get('/citas'),
        ]).then(([paciente, patrones, historial, allSessions, todasCitas]) => {
          const sessions = Array.isArray(allSessions) ? allSessions : [];
          const citas = Array.isArray(todasCitas) ? todasCitas : [];
          // Próximas sesiones del paciente
          const upcoming = citas.filter(c => c.paciente_id === pacienteId && c.estado !== 'completada' && c.estado !== 'cancelada' && c.id !== citaId);
          // Ficha del paciente
          const detalleEl = document.getElementById('sw-paciente-detalle');
          detalleEl.innerHTML = `
            <div class="flex-col gap-6">
              <div class="flex-center gap-10">
                <div class="av av-md av-sage">${initials(paciente.nombre)}</div>
                <div>
                  <div class="fs-14 fw-500">${paciente.nombre}</div>
                  <div class="fs-11 text-3">${paciente.rut || '—'} · ${paciente.edad} años · ${paciente.sesiones_total} sesiones</div>
                </div>
              </div>
              <div class="flex gap-6 flex-wrap">
                ${paciente.diagnostico ? `<span class="badge badge-blue">${paciente.diagnostico}</span>` : ''}
                <span class="badge ${paciente.status === 'Trabajo activo' ? 'badge-green' : 'badge-gray'}">${paciente.status}</span>
              </div>
              ${patrones.length > 0 ? `
                <div class="divider"></div>
                <div class="fs-11 fw-500 text-2 mb-3">Patrones detectados por Klinós IA:</div>
                <div class="flex gap-4 flex-wrap">${patrones.map(pat => `<span class="chip">${pat.patron} (x${pat.frecuencia})</span>`).join('')}</div>
              ` : ''}
              ${upcoming.length > 0 ? `
                <div class="divider"></div>
                <div class="fs-11 fw-500 text-2 mb-3">Próximas sesiones</div>
                <div class="flex-col gap-4">${upcoming.map(u => `
                  <div class="flex-center gap-8 fs-11">
                    <span class="badge badge-green">${u.fecha} ${u.hora}</span>
                    <span class="text-2">${u.tipo_sesion}</span>
                    <span class="text-3">${u.sala}</span>
                  </div>
                `).join('')}</div>
              ` : ''}
            </div>
          `;
          document.getElementById('sw-paciente-info').style.display = 'block';
          // Sesiones anteriores con análisis IA
          const prevSessions = sessions.filter(x => x.paciente_id === pacienteId && x.registro_id && x.id !== citaId);
          const prevEl = document.getElementById('sw-sesiones-previas-lista');
          if (prevSessions.length > 0 || historial.length > 0) {
            let html = '';
            prevSessions.forEach(ps => {
              const intensidadMap = { baja: 'Baja', media: 'Media', alta: 'Alta' };
              const intensidadBadge = ps.analisis
                ? `<span class="ses-intensidad ${ps.intensidad || 'media'}">${intensidadMap[ps.intensidad] || '—'}</span>`
                : '';
              html += `
                <div class="t-line">
                  <div class="t-dot"></div>
                  <span class="t-date">${ps.fecha} ${ps.hora}</span>
                  <div class="flex-1">
                    <div class="fs-11 text-2">${ps.tipo_sesion}</div>
                    ${ps.analisis ? `<div class="fs-10 text-3 mt-2">${ps.analisis}</div>` : ''}
                  </div>
                  ${intensidadBadge}
                </div>
              `;
            });
            historial.forEach(h => {
              html += `
                <div class="t-line">
                  <div class="t-dot"></div>
                  <span class="t-date">${h.fecha}</span>
                  <span class="text-2">${h.contenido}</span>
                </div>
              `;
            });
            prevEl.innerHTML = html;
            document.getElementById('sw-sesiones-previas').style.display = 'block';
          }
        }).catch(e => console.error(e));
      }
    }).catch(e => {
      console.error(e);
      document.getElementById('sw-paciente').textContent = 'Error al cargar';
    });

    // Initialize session if needed
    if (estado === 'pendiente' || !registroId) {
      post('/klinos/sesiones/iniciar', { cita_id: citaId }).then(data => {
        sesionActualId = data.id;
        document.getElementById('btn-cerrar-sesion').dataset.registroId = data.id;
      });
    } else {
      sesionActualId = registroId;
      document.getElementById('btn-cerrar-sesion').dataset.registroId = registroId;
      fetch(API + '/klinos/sesiones/' + registroId, { method: 'GET', headers: getHeaders() })
        .then(r => r.json().catch(() => ({})))
        .then(d => { if (d.notas) document.getElementById('sw-notas').value = d.notas; })
        .catch(() => {});
    }
  };

  window.guardarBorrador = async function () {
    if (!sesionActualId) return showToast('Primero iniciá la sesión', 'error');
    const notas = document.getElementById('sw-notas').value;
    await put('/klinos/sesiones/' + sesionActualId + '/notas', { notas });
    showToast('Borrador guardado', 'success');
  };

  window.cerrarSesion = async function () {
    if (!sesionActualId) return;
    // Save notes first
    const notas = document.getElementById('sw-notas').value;
    await put('/klinos/sesiones/' + sesionActualId + '/notas', { notas });
    // Close and analyze
    try {
      const res = await post('/klinos/sesiones/' + sesionActualId + '/cerrar');
      document.getElementById('sesion-writing').style.display = 'none';
      document.getElementById('sesion-analisis').style.display = 'flex';
      const intensidadMap = { baja: 'Baja', media: 'Media', alta: 'Alta' };
      function fmtList(text) {
        return text.split('\n').map(r => r.trim()).filter(Boolean).map(r => r.replace(/^-\s*/, ''));
      }
      document.getElementById('analisis-content').innerHTML = `
        <div class="alert alert-sage mb-10">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1L15 14H1L8 1z"/><path d="M8 6v4M8 11.5v.5"/></svg>
          <span><strong>Análisis completado</strong></span>
        </div>
        <div class="fs-12 lh-18 mb-10">${res.analisis || 'No se generó análisis.'}</div>
        <div class="flex-center gap-10 mb-10">
          <span class="fs-11 text-3">Intensidad para el terapeuta:</span>
          <span class="ses-intensidad ${res.intensidad || 'media'}">${intensidadMap[res.intensidad] || 'Media'}</span>
        </div>
        ${res.recomendaciones ? `
          <div class="divider mb-8"></div>
          <div class="fs-12 fw-600 mb-6">Recomendaciones clínicas</div>
          <div class="fs-11 lh-18 text-2">${fmtList(res.recomendaciones).map(r => `<div class="flex gap-6 mb-3"><span style="color:var(--green)">→</span><span>${r}</span></div>`).join('')}</div>
        ` : ''}
        ${res.patologias ? `
          <div class="divider mb-8"></div>
          <div class="fs-12 fw-600 mb-6">Posibles patologías / problemas psicológicos</div>
          <div class="flex gap-4 flex-wrap">${fmtList(res.patologias).map(r => `<span class="badge badge-amber">${r}</span>`).join('')}</div>
        ` : ''}
      `;
      sesionActualId = null;
    } catch (e) {
      showToast('Error al cerrar: ' + e.message, 'error');
    }
  };

  window.cerrarPanelEscritura = function () {
    sesionActualId = null;
    document.getElementById('sesion-writing').style.display = 'none';
    document.getElementById('sesiones-grid').style.display = 'grid';
    const info = document.getElementById('sw-paciente-info');
    if (info) info.style.display = 'none';
    const prev = document.getElementById('sw-sesiones-previas');
    if (prev) { prev.style.display = 'none'; prev.innerHTML = ''; }
  };

  window.cerrarAnalisis = function () {
    document.getElementById('sesion-analisis').style.display = 'none';
    document.getElementById('sesiones-grid').style.display = 'grid';
    loadSesiones();
  };

  // ─── Color picker ───
  window.cambiarColorTema = function (hex) {
    document.documentElement.style.setProperty('--theme-primary', hex);
    document.getElementById('cfg-color-label').textContent = hex;
    // Also override green vars for consistency
    document.documentElement.style.setProperty('--green', hex);
    // Compute a darker shade for dark variants
    const r = parseInt(hex.slice(1,3), 16);
    const g = parseInt(hex.slice(3,5), 16);
    const b = parseInt(hex.slice(5,7), 16);
    const darkR = Math.max(0, r - 40);
    const darkG = Math.max(0, g - 40);
    const darkB = Math.max(0, b - 40);
    const darkHex = '#' + [darkR, darkG, darkB].map(x => x.toString(16).padStart(2,'0')).join('');
    document.documentElement.style.setProperty('--green-dark', darkHex);
    // Save to config
    put('/config', { settings: { theme_color: hex } }).catch(() => {});
    localStorage.setItem('klinos_theme', hex);
  };

  window.cambiarColorSidebar = function (hex) {
    document.documentElement.style.setProperty('--sidebar-bg', hex);
    document.getElementById('cfg-sidebar-color-label').textContent = hex;
    put('/config', { settings: { theme_sidebar_color: hex } }).catch(() => {});
    localStorage.setItem('klinos_sidebar', hex);
  };

  async function applyThemeColor() {
    const saved = localStorage.getItem('klinos_theme');
    if (saved) {
      document.documentElement.style.setProperty('--theme-primary', saved);
      document.documentElement.style.setProperty('--green', saved);
      const picker = document.getElementById('cfg-color');
      if (picker) picker.value = saved;
      const label = document.getElementById('cfg-color-label');
      if (label) label.textContent = saved;
    }
    // Also try from config
    try {
      const cfg = await get('/config');
      if (cfg.theme_color && cfg.theme_color !== saved) {
        localStorage.setItem('klinos_theme', cfg.theme_color);
        document.documentElement.style.setProperty('--theme-primary', cfg.theme_color);
        document.documentElement.style.setProperty('--green', cfg.theme_color);
        const picker = document.getElementById('cfg-color');
        if (picker) picker.value = cfg.theme_color;
        const label = document.getElementById('cfg-color-label');
        if (label) label.textContent = cfg.theme_color;
      }
    } catch (e) {}
    // Sidebar color
    const sbSaved = localStorage.getItem('klinos_sidebar');
    if (sbSaved) {
      document.documentElement.style.setProperty('--sidebar-bg', sbSaved);
      const sbPicker = document.getElementById('cfg-sidebar-color');
      if (sbPicker) sbPicker.value = sbSaved;
      const sbLabel = document.getElementById('cfg-sidebar-color-label');
      if (sbLabel) sbLabel.textContent = sbSaved;
    }
    try {
      const cfg = await get('/config');
      if (cfg.theme_sidebar_color && cfg.theme_sidebar_color !== sbSaved) {
        localStorage.setItem('klinos_sidebar', cfg.theme_sidebar_color);
        document.documentElement.style.setProperty('--sidebar-bg', cfg.theme_sidebar_color);
        const sbPicker = document.getElementById('cfg-sidebar-color');
        if (sbPicker) sbPicker.value = cfg.theme_sidebar_color;
        const sbLabel = document.getElementById('cfg-sidebar-color-label');
        if (sbLabel) sbLabel.textContent = cfg.theme_sidebar_color;
      }
    } catch (e) {}
  }

  // ─── Reserva: populate tipo_sesión from API ───
  async function loadTipoSesionOptions() {
    try {
      const tipos = await get('/tipos-terapia');
      const selects = document.querySelectorAll('select');
      // Find tipo_sesion selects (the one in reserva has Psicoterapia etc.)
      for (const sel of selects) {
        if (sel.options.length > 1 && sel.options[1].textContent.includes('Psicoterapia')) {
          const currentVal = sel.value;
          sel.innerHTML = '<option value="">Seleccionar...</option>';
          for (const t of tipos) {
            const opt = document.createElement('option');
            opt.value = t.nombre;
            opt.textContent = t.nombre;
            sel.appendChild(opt);
          }
          if (currentVal) sel.value = currentVal;
          break;
        }
      }
    } catch (e) {
      console.error('Error cargando tipos de terapia', e);
    }
  }

  // ─── Terapias ───
  async function loadTerapias() {
    try {
      const tipos = await get('/tipos-terapia');
      const tbody = document.getElementById('terapias-list');
      if (!tbody) return;
      if (tipos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="fs-12 text-3" style="padding:20px;text-align:center">No hay tipos de terapia registrados</td></tr>';
        return;
      }
      tbody.innerHTML = tipos.map(t => `
        <tr>
          <td>${t.nombre}</td>
          <td class="text-3 fs-11">${t.descripcion || '-'}</td>
          <td>${t.duracion_default} min</td>
          <td><span style="display:inline-block;width:20px;height:20px;border-radius:4px;background:${t.color}"></span></td>
          <td>${t.activo ? '<span class="badge badge-green">Activo</span>' : '<span class="badge badge-gray">Inactivo</span>'}</td>
          <td>
            <button class="btn-outline btn-xs" onclick="editarTerapia(${t.id})">Editar</button>
            <button class="btn-danger btn-xs" onclick="eliminarTerapia(${t.id})">Eliminar</button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.error('Error cargando terapias', e);
    }
  }

  window.mostrarFormTerapia = function () {
    document.getElementById('tf-id').value = '';
    document.getElementById('tf-nombre').value = '';
    document.getElementById('tf-descripcion').value = '';
    document.getElementById('tf-duracion').value = '50';
    document.getElementById('tf-color').value = '#3E8E6B';
    document.getElementById('terapia-form').style.display = 'block';
  };

  window.cancelarFormTerapia = function () {
    document.getElementById('terapia-form').style.display = 'none';
  };

  window.guardarTerapia = async function () {
    const id = document.getElementById('tf-id').value;
    const data = {
      nombre: document.getElementById('tf-nombre').value.trim(),
      descripcion: document.getElementById('tf-descripcion').value.trim(),
      duracion_default: parseInt(document.getElementById('tf-duracion').value) || 50,
      color: document.getElementById('tf-color').value,
      activo: document.getElementById('tf-activo') ? document.getElementById('tf-activo').checked : true,
    };
    if (!data.nombre) { alert('El nombre es obligatorio'); return; }
    try {
      if (id) {
        await put('/tipos-terapia/' + id, data);
      } else {
        await post('/tipos-terapia', data);
      }
      document.getElementById('terapia-form').style.display = 'none';
      loadTerapias();
      loadTipoSesionOptions();
    } catch (e) {
      alert('Error: ' + e.message);
    }
  };

  window.editarTerapia = async function (id) {
    try {
      const t = await get('/tipos-terapia/' + id);
      document.getElementById('tf-id').value = id;
      document.getElementById('tf-nombre').value = t.nombre;
      document.getElementById('tf-descripcion').value = t.descripcion || '';
      document.getElementById('tf-duracion').value = t.duracion_default;
      document.getElementById('tf-color').value = t.color;
      const cb = document.getElementById('tf-activo');
      if (cb) cb.checked = t.activo;
      document.getElementById('terapia-form').style.display = 'block';
    } catch (e) {
      alert('Error: ' + e.message);
    }
  };

  window.eliminarTerapia = async function (id) {
    if (!confirm('¿Eliminar este tipo de terapia?')) return;
    try {
      await del('/tipos-terapia/' + id);
      loadTerapias();
    } catch (e) {
      alert('Error: ' + e.message);
    }
  };

  // ─── Font size ───
  window.cambiarFontSize = function (px) {
    const scale = px / 14;
    document.documentElement.style.setProperty('--font-scale', scale);
    document.getElementById('cfg-font-size-label').textContent = px + 'px';
    localStorage.setItem('klinos_font_size', px);
  };

  function applyFontSize() {
    const saved = localStorage.getItem('klinos_font_size');
    if (saved) {
      const scale = parseInt(saved) / 14;
      document.documentElement.style.setProperty('--font-scale', scale);
      const slider = document.getElementById('cfg-font-size');
      if (slider) slider.value = saved;
      const label = document.getElementById('cfg-font-size-label');
      if (label) label.textContent = saved + 'px';
    }
  }

  // ─── User creation ───
  window.mostrarFormUsuario = function () {
    document.getElementById('nuevo-usuario-form').style.display = 'block';
  };

  window.cancelarFormUsuario = function () {
    document.getElementById('nuevo-usuario-form').style.display = 'none';
  };

  window.guardarNuevoUsuario = async function () {
    const nombre = document.getElementById('nu-nombre').value.trim();
    const username = document.getElementById('nu-username').value.trim();
    const email = document.getElementById('nu-email').value.trim();
    const password = document.getElementById('nu-password').value.trim();
    const rol = document.getElementById('nu-rol').value;
    if (!nombre || !username || !password) {
      alert('Nombre, username y contraseña son obligatorios');
      return;
    }
    const permPresets = {
      admin: '{"dashboard":"view_edit","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view_edit","citas":"view_edit","finanzas":"view_edit","eventos":"view_edit","cursos":"view_edit","miembros":"view_edit","klinos":"view_edit","config":"view_edit","historial":"view_edit","carga":"view_edit"}',
      terapeuta: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view","eventos":"view","cursos":"view","miembros":"view","klinos":"view_edit","config":"hide","historial":"view_edit","carga":"view_edit"}',
      recepcion: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view_edit","eventos":"view","cursos":"view","miembros":"view","klinos":"hide","config":"hide","historial":"hide","carga":"hide"}',
    };
    try {
      await post('/auth/register', { username, password, nombre, email, rol, permissions: permPresets[rol] });
      showToast('Usuario creado', 'success');
      document.getElementById('nuevo-usuario-form').style.display = 'none';
      loadUsers();
    } catch (e) {
      showToast('Error: ' + e.message, 'error');
    }
  };

  // ─── Init ───
  async function init() {
    // Apply dark mode before login if previously set
    if (localStorage.getItem('klinos_dark') === 'true') {
      document.documentElement.classList.add('dark');
    }
    // Check for saved session
    const savedUser = localStorage.getItem('klinos_user');
    if (token && savedUser) {
      try {
        currentUser = JSON.parse(savedUser);
        const user = await get('/auth/me');
        currentUser = user;
        localStorage.setItem('klinos_user', JSON.stringify(user));
        document.getElementById('login-overlay').classList.add('hidden');
        applyPermissions(user.permissions);
        updateSidebarUser(user);
        loadDashboard();
        loadPacientesList();
        loadConfig();
        applyDarkMode();
        applyThemeColor();
        applyFontSize();
        loadTipoSesionOptions();
        return;
      } catch (e) {
        token = '';
        localStorage.removeItem('klinos_token');
        localStorage.removeItem('klinos_user');
      }
    }

    // Press Enter to login
    document.getElementById('login-pass').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') login();
    });
    document.getElementById('login-user').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') document.getElementById('login-pass').focus();
    });

    // Tab switching
    document.querySelectorAll('.tabs').forEach(tabGroup => {
      tabGroup.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function () {
          tabGroup.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
          this.classList.add('active');
        });
      });
    });

    // Reserva form
    const reservaBtn = document.querySelector('#p-reservar .btn-primary');
    if (reservaBtn) {
      reservaBtn.addEventListener('click', function () {
        const panel = document.getElementById('p-reservar');
        const selects = panel.querySelectorAll('select');
        const inputs = panel.querySelectorAll('input');
        const textarea = panel.querySelector('textarea');
        const data = {
          paciente_id: selects[0].selectedIndex,
          terapeuta_id: selects[1].selectedIndex,
          fecha: inputs[0].value,
          hora: selects[2].value,
          tipo_sesion: selects[3].value,
          sala: selects[4].value,
          notas: textarea.value,
          duracion: 50,
          estado: 'confirmada',
        };
        submitReserva(data);
      });
    }

    // Invite member
    const inviteBtn = document.querySelector('#p-miembros .btn-primary');
    if (inviteBtn) {
      inviteBtn.addEventListener('click', async function () {
        const panel = document.getElementById('p-miembros');
        const email = panel.querySelector('input[type="email"]').value;
        const rol = panel.querySelector('select').value;
        if (!email) return showToast('Ingresa un email', 'error');
        await post('/miembros', {
          nombre: email.split('@')[0],
          email: email,
          rol: rol,
          fecha_ingreso: new Date().toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\./g, ''),
          avatar_color: ['blue', 'sage', 'rose', 'amber'][Math.floor(Math.random() * 4)],
        });
        showToast('Invitación enviada', 'success');
        loadMiembros();
      });
    }
  }

  async function submitReserva(data) {
    try {
      await post('/citas', data);
      showToast('Cita reservada con éxito', 'success');
      nav('agenda', document.querySelector('[onclick*="agenda"]'));
    } catch (e) {
      showToast('Error al reservar: ' + e.message, 'error');
    }
  }

  // ─── Role management ───
  async function loadUsers() {
    if (!canView('configuracion')) return;
    try {
      const users = await get('/auth/users');
      const el = document.getElementById('users-list');
      if (!el) return;
      const roleOptions = ['admin', 'terapeuta', 'recepcion'];
      const permPresets = {
        admin: '{"dashboard":"view_edit","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view_edit","citas":"view_edit","finanzas":"view_edit","eventos":"view_edit","cursos":"view_edit","miembros":"view_edit","klinos":"view_edit","config":"view_edit","historial":"view_edit","carga":"view_edit"}',
        terapeuta: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view","eventos":"view","cursos":"view","miembros":"view","klinos":"view_edit","config":"hide","historial":"view_edit","carga":"view_edit"}',
        recepcion: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view_edit","eventos":"view","cursos":"view","miembros":"view","klinos":"hide","config":"hide","historial":"hide","carga":"hide"}',
      };
      el.innerHTML = users.map(u => `
        <tr>
          <td><strong>${u.nombre}</strong><div class="fs-10 text-3">@${u.username}</div></td>
          <td>
            <select class="user-role" data-user-id="${u.id}" onchange="updateUserRole(${u.id}, this.value)">
              ${roleOptions.map(r => `<option value="${r}" ${u.rol === r ? 'selected' : ''}>${r.charAt(0).toUpperCase() + r.slice(1)}</option>`).join('')}
            </select>
          </td>
          <td><button class="btn-outline btn-sm" onclick="showUserPerms(${u.id})">Editar permisos</button></td>
          <td><span class="badge ${u.rol === 'admin' ? 'badge-blue' : u.rol === 'terapeuta' ? 'badge-green' : 'badge-amber'}">${u.rol}</span></td>
        </tr>
      `).join('');
    } catch (e) { console.error(e); }
  }

  window.updateUserRole = async function (userId, newRole) {
    const permPresets = {
      admin: '{"dashboard":"view_edit","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view_edit","citas":"view_edit","finanzas":"view_edit","eventos":"view_edit","cursos":"view_edit","miembros":"view_edit","klinos":"view_edit","config":"view_edit","historial":"view_edit","carga":"view_edit"}',
      terapeuta: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view","eventos":"view","cursos":"view","miembros":"view","klinos":"view_edit","config":"hide","historial":"view_edit","carga":"view_edit"}',
      recepcion: '{"dashboard":"view","agenda":"view_edit","reservar":"view_edit","pacientes":"view_edit","terapeutas":"view","citas":"view_edit","finanzas":"view_edit","eventos":"view","cursos":"view","miembros":"view","klinos":"hide","config":"hide","historial":"hide","carga":"hide"}',
    };
    try {
      await put('/auth/users/' + userId, {
        rol: newRole,
        permissions: permPresets[newRole] || permPresets.terapeuta,
      });
      showToast('Rol actualizado', 'success');
      loadUsers();
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
  };

  window.showUserPerms = function (userId) {
    const row = document.querySelector(`.user-role[data-user-id="${userId}"]`).closest('tr');
    const permsRow = row.nextElementSibling;
    if (permsRow && permsRow.classList.contains('user-perms-row')) {
      permsRow.remove();
      return;
    }
    // Fetch current perms
    fetch(API + '/auth/users/' + userId, { headers: getHeaders() })
      .then(r => r.json())
      .then(u => {
        let perms;
        try { perms = JSON.parse(u.permissions); } catch (e) { perms = {}; }
        const form = document.createElement('tr');
        form.className = 'user-perms-row';
        form.innerHTML = `<td colspan="4" style="padding:10px 14px;background:var(--slate-light)">
          <div class="fs-11 fw-500 mb-8">Permisos para <strong>${u.nombre}</strong></div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;max-width:500px">
            ${Object.keys(perms).sort().map(k => `
              <label style="font-weight:400;font-size:11px;display:flex;align-items:center;gap:4px;cursor:pointer">
                <input type="checkbox" ${perms[k] !== 'hide' ? 'checked' : ''} data-perm-key="${k}" style="width:auto"> ${k}
              </label>
            `).join('')}
          </div>
          <div class="flex gap-8 mt-8">
            <button class="btn-primary btn-sm" onclick="saveUserPerms(${userId})">Guardar permisos</button>
            <button class="btn-outline btn-sm" onclick="this.closest('tr').remove()">Cancelar</button>
          </div>
        </td>`;
        row.parentNode.insertBefore(form, row.nextSibling);
      });
  };

  window.saveUserPerms = async function (userId) {
    const permsRow = document.querySelector(`.user-perms-row`);
    if (!permsRow) return;
    const checkboxes = permsRow.querySelectorAll('[data-perm-key]');
    const perms = {};
    checkboxes.forEach(cb => {
      perms[cb.dataset.permKey] = cb.checked ? 'view_edit' : 'hide';
    });
    try {
      await put('/auth/users/' + userId, { permissions: JSON.stringify(perms) });
      showToast('Permisos actualizados', 'success');
      permsRow.remove();
      loadUsers();
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
  };

  // ─── Groq / Klinós Chat ───
  window.sendKlinosChat = async function () {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    const log = document.getElementById('chat-log');
    log.innerHTML += `<div class="chat-msg chat-user"><strong>Tú:</strong> ${msg}</div>`;
    input.value = '';
    log.scrollTop = log.scrollHeight;
    log.innerHTML += `<div class="chat-msg chat-loading"><em>Klinós IA está pensando...</em></div>`;
    log.scrollTop = log.scrollHeight;
    // Find selected paciente
    const select = document.getElementById('chat-paciente');
    const pacienteId = parseInt(select?.value || '0');
    try {
      const res = await post('/klinos/chat', { message: msg, paciente_id: pacienteId });
      log.querySelector('.chat-loading')?.remove();
      log.innerHTML += `<div class="chat-msg chat-ai"><strong>Klinós IA:</strong> ${res.reply}</div>`;
      log.scrollTop = log.scrollHeight;
    } catch (e) {
      log.querySelector('.chat-loading')?.remove();
      log.innerHTML += `<div class="chat-msg chat-ai"><strong>Klinós IA:</strong> Error: ${e.message}</div>`;
    }
  };

  // ─── Save Groq API key ───
  window.saveGroqKey = async function () {
    const key = document.getElementById('cfg-groq-key').value.trim();
    try {
      await put('/config', { settings: { groq_api_key: key } });
      showToast('API key guardada', 'success');
    } catch (e) { showToast('Error: ' + e.message, 'error'); }
  };

  document.addEventListener('DOMContentLoaded', init);

})();
