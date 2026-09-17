import { useState } from 'react'

type ModuleKey = 'dashboard' | 'planning' | 'calendar' | 'routes' | 'fleet' | 'expenses' | 'documents' | 'execution'

const modules: Array<{ key: ModuleKey; label: string; icon: string }> = [
  { key: 'dashboard', label: 'Dashboard', icon: '⌂' },
  { key: 'planning', label: 'Planeación', icon: '◫' },
  { key: 'calendar', label: 'Calendario', icon: '▦' },
  { key: 'routes', label: 'Rutas', icon: '⌁' },
  { key: 'fleet', label: 'Flotilla', icon: '▰' },
  { key: 'expenses', label: 'Viáticos', icon: '$' },
  { key: 'documents', label: 'Documentos', icon: '▤' },
  { key: 'execution', label: 'Ejecución', icon: '✓' },
]

const services = [
  { time: '08:30', code: 'SRV-0261', client: 'Estación Puebla Norte', type: 'Inspección normativa', status: 'EN RUTA', unit: 'FLC-014' },
  { time: '10:00', code: 'SRV-0264', client: 'Gasolinera Cholula', type: 'Verificación documental', status: 'CONFIRMADO', unit: 'FLC-009' },
  { time: '13:30', code: 'SRV-0268', client: 'Estación San Martín', type: 'Toma de muestras', status: 'PROGRAMADO', unit: 'FLC-017' },
  { time: '16:00', code: 'SRV-0270', client: 'Terminal Tehuacán', type: 'Visita técnica', status: 'PROGRAMADO', unit: 'FLC-011' },
]

const fleet = [
  { unit: 'FLC-014', vehicle: 'Toyota Hilux', driver: 'J. Hernández', km: '84,210 km', state: 'EN RUTA', tone: 'route' },
  { unit: 'FLC-009', vehicle: 'Nissan NP300', driver: 'M. García', km: '61,842 km', state: 'ASIGNADO', tone: 'assigned' },
  { unit: 'FLC-017', vehicle: 'Ford Ranger', driver: 'A. López', km: '42,110 km', state: 'DISPONIBLE', tone: 'available' },
  { unit: 'FLC-011', vehicle: 'Toyota Hilux', driver: 'R. Pérez', km: '96,334 km', state: 'MANTENIMIENTO', tone: 'maintenance' },
]

const alerts = [
  { level: 'critical', title: 'Mantenimiento próximo', detail: 'FLC-011 · servicio preventivo en 790 km' },
  { level: 'warning', title: 'Viático pendiente', detail: 'TRP-0142 · requiere autorización' },
  { level: 'warning', title: 'Documento por vencer', detail: 'FLC-009 · póliza vehicular en 12 días' },
]

function App() {
  const [active, setActive] = useState<ModuleKey>('dashboard')
  const [search, setSearch] = useState('')

  const currentModule = modules.find((module) => module.key === active) ?? modules[0]

  return (
    <div className="logistics-app">
      <aside className="logistics-sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">LP</div>
          <div>
            <strong>LOGISTICS</strong>
            <span>OPERATIONS PLATFORM</span>
          </div>
        </div>

        <div className="sidebar-section-label">OPERACIÓN</div>
        <nav className="sidebar-nav" aria-label="Módulos de logística">
          {modules.map((module) => (
            <button
              key={module.key}
              className={`sidebar-item ${active === module.key ? 'is-active' : ''}`}
              onClick={() => setActive(module.key)}
            >
              <span className="sidebar-icon" aria-hidden="true">{module.icon}</span>
              <span>{module.label}</span>
              {module.key === 'expenses' && <b className="nav-count">4</b>}
            </button>
          ))}
        </nav>

        <div className="sidebar-spacer" />
        <div className="system-status">
          <span className="status-led" />
          <div>
            <strong>SISTEMA OPERATIVO</strong>
            <small>API · DATABASE · MAPS</small>
          </div>
        </div>
      </aside>

      <main className="logistics-main">
        <header className="logistics-topbar">
          <div className="topbar-context">
            <span>LOGISTICS / OPERATIONS</span>
            <strong>{currentModule.label}</strong>
          </div>
          <div className="topbar-actions">
            <label className="global-search">
              <span aria-hidden="true">⌕</span>
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar operación, unidad, cliente..." />
            </label>
            <button className="icon-button" aria-label="Notificaciones">◌<i /></button>
            <div className="user-chip">
              <div className="user-avatar">LC</div>
              <div><strong>Administrador</strong><small>OPERACIONES</small></div>
            </div>
          </div>
        </header>

        {active === 'dashboard' ? <Dashboard onNavigate={setActive} /> : <ModuleView module={currentModule} />}
      </main>
    </div>
  )
}

function Dashboard({ onNavigate }: { onNavigate: (module: ModuleKey) => void }) {
  return (
    <div className="page-shell">
      <section className="logistics-hero">
        <div className="hero-content">
          <span className="eyebrow">CENTRO DE CONTROL · OPERACIÓN TERRESTRE</span>
          <h1>Operación logística</h1>
          <p>Planea servicios, administra rutas, controla flotilla y documenta viáticos desde un solo centro operativo.</p>
        </div>
        <div className="hero-actions">
          <div className="hero-summary"><small>HOY</small><strong>17</strong><span>servicios</span></div>
          <button className="primary-action" onClick={() => onNavigate('planning')}><span>＋</span> Programar servicio</button>
        </div>
      </section>

      <section className="kpi-grid">
        <Kpi label="Servicios hoy" value="17" meta="12 confirmados" icon="▦" accent="orange" />
        <Kpi label="Viajes activos" value="06" meta="03 en ruta ahora" icon="⌁" accent="blue" />
        <Kpi label="Flotilla disponible" value="09 / 14" meta="64% disponibilidad" icon="▰" accent="green" />
        <Kpi label="Viáticos pendientes" value="$28,450" meta="04 autorizaciones" icon="$" accent="red" />
      </section>

      <section className="dashboard-grid">
        <div className="hardware-panel map-panel">
          <PanelHeader eyebrow="MONITOREO GEOGRÁFICO" title="Mapa operativo" action="Ver mapa completo" onAction={() => onNavigate('routes')} />
          <div className="map-surface">
            <div className="map-grid-lines" />
            <div className="map-road road-a" /><div className="map-road road-b" /><div className="map-road road-c" />
            <div className="map-route route-one" /><div className="map-route route-two" />
            <MapPin className="pin-a" label="PUEBLA" status="active" />
            <MapPin className="pin-b" label="CHOLULA" status="active" />
            <MapPin className="pin-c" label="TEHUACÁN" status="idle" />
            <div className="map-overlay"><strong>06</strong><span>UNIDADES EN OPERACIÓN</span></div>
            <div className="map-controls"><button>＋</button><button>−</button><button>⌖</button></div>
          </div>
        </div>

        <div className="hardware-panel agenda-panel">
          <PanelHeader eyebrow="AGENDA OPERATIVA" title="Servicios de hoy" action="Ver calendario" onAction={() => onNavigate('calendar')} />
          <div className="agenda-list">
            {services.map((service) => (
              <div className="agenda-row" key={service.code}>
                <time>{service.time}</time>
                <div className="agenda-marker"><span /></div>
                <div className="agenda-main"><strong>{service.client}</strong><span>{service.code} · {service.type}</span></div>
                <div className="agenda-side"><em className={`status status-${service.status.replace(' ', '-').toLowerCase()}`}>{service.status}</em><small>{service.unit}</small></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="dashboard-grid lower-grid">
        <div className="hardware-panel">
          <PanelHeader eyebrow="CONTROL DE FLOTA" title="Estado de unidades" action="Administrar flotilla" onAction={() => onNavigate('fleet')} />
          <div className="fleet-table">
            <div className="fleet-table-head"><span>UNIDAD</span><span>VEHÍCULO / CONDUCTOR</span><span>KILOMETRAJE</span><span>ESTADO</span></div>
            {fleet.map((item) => <div className="fleet-row" key={item.unit}><strong>{item.unit}</strong><div><b>{item.vehicle}</b><small>{item.driver}</small></div><span>{item.km}</span><em className={`fleet-state ${item.tone}`}>{item.state}</em></div>)}
          </div>
        </div>

        <div className="hardware-panel alerts-panel">
          <PanelHeader eyebrow="CONTROL DE RIESGOS" title="Alertas operativas" action="Ver todas" onAction={() => onNavigate('documents')} />
          <div className="alert-list">
            {alerts.map((alert) => <div className="alert-row" key={alert.title}><span className={`alert-dot ${alert.level}`} /><div><strong>{alert.title}</strong><small>{alert.detail}</small></div><button aria-label="Abrir alerta">›</button></div>)}
          </div>
          <div className="alert-footer"><span>Última sincronización</span><strong>Hoy · 13:42:08</strong></div>
        </div>
      </section>
    </div>
  )
}

function Kpi({ label, value, meta, icon, accent }: { label: string; value: string; meta: string; icon: string; accent: string }) {
  return <article className={`kpi-card accent-${accent}`}><div className="kpi-icon">{icon}</div><div><small>{label}</small><strong>{value}</strong><span>{meta}</span></div></article>
}

function PanelHeader({ eyebrow, title, action, onAction }: { eyebrow: string; title: string; action: string; onAction: () => void }) {
  return <div className="panel-header"><div><span>{eyebrow}</span><h2>{title}</h2></div><button onClick={onAction}>{action} <b>→</b></button></div>
}

function MapPin({ className, label, status }: { className: string; label: string; status: 'active' | 'idle' }) {
  return <div className={`map-pin ${className}`}><span className={status} /><label>{label}</label></div>
}

function ModuleView({ module }: { module: { label: string; icon: string } }) {
  const cards = [
    ['Planeación', 'Servicios, asignaciones y programación de recorridos.'],
    ['Calendario', 'Vista operativa de servicios y disponibilidad.'],
    ['Rutas', 'Planificación terrestre, paradas y seguimiento.'],
    ['Flotilla', 'Unidades, kilometraje, combustible y mantenimiento.'],
    ['Viáticos', 'Presupuestos, casetas, combustible y comprobantes.'],
    ['Documentos', 'Expedientes, versiones, evidencias y PDF.'],
    ['Ejecución', 'Check-in, check-out y evidencia de servicio.'],
  ]
  const current = cards.find(([title]) => title === module.label)
  return <div className="page-shell module-shell"><section className="logistics-hero"><div className="hero-content"><span className="eyebrow">MÓDULO OPERATIVO</span><h1>{module.icon} {module.label}</h1><p>{current?.[1] ?? 'Centro de control operacional de Logistics Platform.'}</p></div><button className="primary-action"><span>＋</span> Nueva operación</button></section><div className="module-grid"><article className="hardware-panel module-card"><span className="module-card-icon">{module.icon}</span><span className="eyebrow">DATA READY</span><h2>Vista preparada para API</h2><p>La interfaz mantiene PostgreSQL como Source of Truth. Este módulo queda preparado para conectar endpoints Django REST sin trasladar lógica operativa al frontend.</p><div className="module-meta"><span>ESTADO</span><strong>INTERFAZ OPERATIVA</strong></div></article><article className="hardware-panel module-card"><span className="eyebrow">ARQUITECTURA</span><h2>Flujo de información</h2><div className="flow"><span>POSTGRESQL</span><b>→</b><span>DJANGO REST</span><b>→</b><span>FRONTEND</span></div><p>Mapas, calendario y documentos funcionan como vistas/proyecciones de registros persistidos.</p></article></div></div>
}

export default App
