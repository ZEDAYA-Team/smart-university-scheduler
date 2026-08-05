"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle, BarChart3, Bell, Building2, CalendarDays, CheckCircle2,
  ChevronDown, Download, FileText, LayoutDashboard, Menu, MoreHorizontal,
  Search, Settings, Users, X
} from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const utilization = [
  { room: "CNCS-201", value: 91 }, { room: "CNCS-104", value: 84 },
  { room: "Lab-3", value: 78 }, { room: "CNCS-305", value: 65 },
  { room: "Lab-1", value: 54 },
];

const departments = [
  { name: "Computer Science", value: 34, color: "#5b5bd6" },
  { name: "Mathematics", value: 27, color: "#8b8be8" },
  { name: "Physics", value: 21, color: "#b6b6f4" },
  { name: "Others", value: 18, color: "#e2e4f5" },
];

const conflicts = [
  { type: "Room overlap", item: "CNCS-201 · Tuesday 10:00", status: "Open", tone: "danger" },
  { type: "Capacity exceeded", item: "STAT-2A · Lab-1", status: "Open", tone: "danger" },
  { type: "Lecturer availability", item: "Dr. M. Assefa · Monday 14:00", status: "Review", tone: "warning" },
];

const reports = [
  ["Room utilization", "Weekly capacity and occupancy by room", "Updated 2 min ago"],
  ["Lecturer workload", "Assigned hours against teaching load", "Updated 2 min ago"],
  ["Conflict audit", "Unresolved and resolved scheduling conflicts", "Updated today"],
];

export default function Dashboard() {
  const [active, setActive] = useState("Dashboard");
  const [semester, setSemester] = useState("Semester I · 2026/27");
  const [exported, setExported] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [search, setSearch] = useState("");
  const filteredReports = useMemo(() => reports.filter(([name]) => name.toLowerCase().includes(search.toLowerCase())), [search]);

  function exportReport(name: string) {
    const content = `SUTMS ${name}\n${semester}\nGenerated: ${new Date().toLocaleString()}\n\nThis demo export is ready to be connected to the FastAPI reporting endpoint.`;
    const url = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `${name.toLowerCase().replaceAll(" ", "-")}.txt`; anchor.click();
    URL.revokeObjectURL(url); setExported(name); window.setTimeout(() => setExported(null), 2500);
  }

  const nav = ["Dashboard", "Timetable", "Conflicts", "Reports"];
  return (
    <main className="shell">
      <aside className={mobileOpen ? "sidebar open" : "sidebar"}>
        <div className="brand"><div className="brandmark">S</div><span>SUTMS</span><button className="close" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={18}/></button></div>
        <div className="nav-label">WORKSPACE</div>
        <nav>{nav.map((item, index) => <button key={item} onClick={() => { setActive(item); setMobileOpen(false); }} className={active === item ? "nav-item selected" : "nav-item"}>{[<LayoutDashboard key="d"/>, <CalendarDays key="t"/>, <AlertTriangle key="c"/>, <FileText key="r"/>][index]}{item}{item === "Conflicts" && <em>3</em>}</button>)}</nav>
        <div className="nav-label management">MANAGEMENT</div>
        <nav><button className="nav-item"><Users/>Users</button><button className="nav-item"><Building2/>Resources</button><button className="nav-item"><Settings/>Settings</button></nav>
        <div className="profile"><div className="avatar">AB</div><div><strong>Abel Bekele</strong><small>System Administrator</small></div><MoreHorizontal size={18}/></div>
      </aside>
      {mobileOpen && <button className="scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}

      <section className="content">
        <header><button className="menu" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu/></button><div className="crumb">Workspace <span>/</span> {active}</div><div className="header-actions"><button className="notification" aria-label="Notifications"><Bell size={20}/><i/></button><button className="semester">{semester}<ChevronDown size={16}/></button></div></header>
        <div className="page-title"><div><p className="eyebrow">OVERVIEW</p><h1>{active === "Dashboard" ? "Dashboard" : active}</h1><p className="sub">CNCS pilot · Addis Ababa University</p></div><button className="primary" onClick={() => exportReport("Dashboard summary")}><Download size={17}/>Export summary</button></div>

        <section className="metrics">
          <Metric icon={<CalendarDays/>} label="Scheduled sessions" value="248" detail="12 more than last week" positive />
          <Metric icon={<Building2/>} label="Avg. room utilization" value="73.6%" detail="Across 18 active rooms" />
          <Metric icon={<Users/>} label="Lecturers on schedule" value="62" detail="4 are near load limit" />
          <Metric icon={<AlertTriangle/>} label="Open conflicts" value="3" detail="Requires review" alert />
        </section>

        <section className="grid two-col">
          <article className="card chart-card"><div className="card-head"><div><h2>Room utilization</h2><p>Used hours / available hours this week</p></div><button className="icon-button" onClick={() => exportReport("Room utilization")} aria-label="Export room utilization"><Download size={17}/></button></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={utilization} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}><CartesianGrid vertical={false} stroke="#edf0f6"/><XAxis dataKey="room" axisLine={false} tickLine={false} tick={{ fill: "#7a8194", fontSize: 12 }}/><YAxis unit="%" axisLine={false} tickLine={false} tick={{ fill: "#7a8194", fontSize: 12 }}/><Tooltip cursor={{ fill: "#f4f5fe" }} formatter={(value) => [`${value}%`, "Utilization"]}/><Bar dataKey="value" radius={[5,5,0,0]} fill="#5b5bd6" maxBarSize={38}/></BarChart></ResponsiveContainer></div></article>
          <article className="card chart-card"><div className="card-head"><div><h2>Scheduled sessions</h2><p>Distribution by department</p></div><button className="icon-button" onClick={() => exportReport("Department sessions")} aria-label="Export department sessions"><Download size={17}/></button></div><div className="donut-row"><ResponsiveContainer width="48%" height={220}><PieChart><Pie data={departments} dataKey="value" nameKey="name" innerRadius={62} outerRadius={87} paddingAngle={3}>{departments.map((entry) => <Cell key={entry.name} fill={entry.color}/>)}</Pie><Tooltip formatter={(value) => [`${value}%`, "Share"]}/></PieChart></ResponsiveContainer><div className="legend">{departments.map(x => <div key={x.name}><span style={{ background: x.color }}/><p>{x.name}<b>{x.value}%</b></p></div>)}</div></div></article>
        </section>

        <section className="grid two-col lower">
          <article className="card"><div className="card-head"><div><h2>Conflict watch</h2><p>Latest conflicts detected in the current timetable</p></div><button className="text-button" onClick={() => setActive("Conflicts")}>View all</button></div><div className="conflicts">{conflicts.map(c => <div className="conflict" key={c.item}><div className={`conflict-icon ${c.tone}`}><AlertTriangle size={17}/></div><div><strong>{c.type}</strong><p>{c.item}</p></div><span className={`status ${c.tone}`}>{c.status}</span></div>)}</div></article>
          <article className="card"><div className="card-head"><div><h2>Lecturer workload</h2><p>Teaching load status for this semester</p></div><button className="text-button" onClick={() => exportReport("Lecturer workload")}>Full report</button></div><div className="workload"><Workload name="Dr. Meron Assefa" course="CS · 16 / 18 hours" percent={89}/><Workload name="Dr. Solomon Tadesse" course="Mathematics · 12 / 16 hours" percent={75}/><Workload name="Ms. Selamawit Worku" course="Physics · 10 / 14 hours" percent={71}/></div></article>
        </section>

        <section className="reports"><div className="section-heading"><div><h2>Reports</h2><p>Download ready-to-share operational reports</p></div><div className="search"><Search size={17}/><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search reports"/></div></div><div className="report-list">{filteredReports.map(([name, description, updated]) => <div className="report" key={name}><div className="report-icon"><BarChart3 size={21}/></div><div><strong>{name}</strong><p>{description}</p></div><small>{updated}</small><button className="download" onClick={() => exportReport(name)}><Download size={16}/>Export</button></div>)}{filteredReports.length === 0 && <p className="empty">No reports match “{search}”.</p>}</div></section>
      </section>
      {exported && <div className="toast"><CheckCircle2 size={18}/>{exported} exported</div>}
    </main>
  );
}

function Metric({ icon, label, value, detail, positive, alert }: { icon: React.ReactNode; label: string; value: string; detail: string; positive?: boolean; alert?: boolean }) { return <article className="metric"><div className={alert ? "metric-icon alert" : "metric-icon"}>{icon}</div><p>{label}</p><h2>{value}</h2><small className={positive ? "positive" : alert ? "negative" : ""}>{detail}</small></article>; }
function Workload({ name, course, percent }: { name: string; course: string; percent: number }) { return <div className="worker"><div className="worker-title"><div className="person">{name.split(" ").slice(1).map(n => n[0]).join("")}</div><div><strong>{name}</strong><p>{course}</p></div><b>{percent}%</b></div><div className="progress"><span style={{ width: `${percent}%` }}/></div></div>; }
