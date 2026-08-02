import { useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowUpRight,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  Clock3,
  Cpu,
  Database,
  DoorOpen,
  FileJson,
  Layers3,
  Loader2,
  Plus,
  RefreshCw,
  Sparkles,
  Users,
  X,
} from 'lucide-react';
import {
  getListTimetableRunsQueryKey,
  getGetTimetableRunQueryKey,
  useCreateTimetableRun,
  useGetTimetableRun,
  useListTimetableRuns,
} from '@workspace/api-client-react';
import type {
  CourseOffering,
  ScheduleGenerationRequest,
  SolverConflict,
  TimetableRunDetail,
  TimetableRunSummary,
} from '@workspace/api-client-react';
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import { Route, Switch, Router as WouterRouter, useLocation } from 'wouter';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import NotFound from '@/pages/not-found';

const queryClient = new QueryClient();

const starterSchedule: ScheduleGenerationRequest = {
  timeSlots: [
    { id: 'mon-08', day: 'MON', startMinute: 480, endMinute: 600 },
    { id: 'mon-10', day: 'MON', startMinute: 600, endMinute: 720 },
    { id: 'tue-08', day: 'TUE', startMinute: 480, endMinute: 600 },
    { id: 'tue-10', day: 'TUE', startMinute: 600, endMinute: 720 },
    { id: 'wed-08', day: 'WED', startMinute: 480, endMinute: 600 },
    { id: 'wed-10', day: 'WED', startMinute: 600, endMinute: 720 },
  ],
  rooms: [
    { id: 'room-a', name: 'CNCS 101', capacity: 60, type: 'LECTURE' },
    { id: 'room-b', name: 'CNCS 204 Lab', capacity: 35, type: 'LAB' },
  ],
  lecturers: [
    {
      id: 'lecturer-1',
      name: 'Dr. Ada Mensah',
      availability: [{ day: 'MON', startMinute: 420, endMinute: 900 }, { day: 'TUE', startMinute: 420, endMinute: 900 }],
    },
    {
      id: 'lecturer-2',
      name: 'Prof. Kwame Owusu',
      availability: [{ day: 'MON', startMinute: 420, endMinute: 900 }, { day: 'WED', startMinute: 420, endMinute: 900 }],
    },
  ],
  sections: [
    { id: 'section-1', name: 'CS-3A', capacity: 40 },
    { id: 'section-2', name: 'CS-3B', capacity: 30 },
  ],
  offerings: [
    {
      id: 'offering-1',
      courseCode: 'CS301',
      courseName: 'Algorithms',
      lecturerId: 'lecturer-1',
      sectionId: 'section-1',
      courseType: 'THEORY',
      studentIds: ['student-1', 'student-2', 'student-3'],
    },
    {
      id: 'offering-2',
      courseCode: 'CS302',
      courseName: 'Database Systems',
      lecturerId: 'lecturer-2',
      sectionId: 'section-2',
      courseType: 'THEORY',
      studentIds: ['student-4', 'student-5', 'student-6'],
    },
    {
      id: 'offering-3',
      courseCode: 'CS305',
      courseName: 'Systems Lab',
      lecturerId: 'lecturer-1',
      sectionId: 'section-1',
      courseType: 'LAB',
      requiredRoomType: 'LAB',
      studentIds: ['student-1', 'student-2', 'student-3'],
    },
  ],
  timeLimitSeconds: 10,
};

const starterJson = JSON.stringify(starterSchedule, null, 2);

function formatTime(minutes: number) {
  const hour = Math.floor(minutes / 60);
  const minute = minutes % 60;
  const suffix = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${String(minute).padStart(2, '0')} ${suffix}`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

function labelForDay(day: string) {
  return day.slice(0, 1) + day.slice(1).toLowerCase();
}

function statusTone(status: string) {
  if (status === 'OPTIMAL' || status === 'published') return 'success';
  if (status === 'FEASIBLE' || status === 'draft') return 'warning';
  if (status === 'INFEASIBLE' || status === 'archived') return 'danger';
  return 'neutral';
}

function StatusBadge({ status }: { status: string }) {
  const tone = statusTone(status);
  const styles = {
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-700',
    danger: 'border-rose-200 bg-rose-50 text-rose-700',
    neutral: 'border-slate-200 bg-slate-50 text-slate-600',
  };
  return (
    <Badge variant="outline" className={`font-semibold uppercase tracking-[0.08em] ${styles[tone]}`}>
      {status}
    </Badge>
  );
}

function EmptyState({ onNew }: { onNew: () => void }) {
  return (
    <div className="flex min-h-[560px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 p-8">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">
          <CalendarClock className="h-7 w-7" />
        </div>
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-blue-700">No timetable drafts yet</p>
        <h2 className="text-2xl font-semibold tracking-tight text-slate-950">Start with a clean scheduling run</h2>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          Load the starter scheduling data, adjust the JSON when needed, and save a versioned draft for review.
        </p>
        <Button className="mt-6" onClick={onNew}>
          <Sparkles className="h-4 w-4" />
          Generate first draft
        </Button>
      </div>
    </div>
  );
}

function RunList({
  runs,
  selectedId,
  onSelect,
  onNew,
  onRefresh,
  isFetching,
}: {
  runs: TimetableRunSummary[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
  onRefresh: () => void;
  isFetching: boolean;
}) {
  return (
    <aside className="flex w-full shrink-0 flex-col border-b border-slate-200 bg-white lg:w-[308px] lg:border-b-0 lg:border-r">
      <div className="border-b border-slate-200 p-5">
        <div className="mb-5 flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">Saved drafts</p>
            <h2 className="mt-2 text-lg font-semibold text-slate-950">Timetable versions</h2>
          </div>
          <Button variant="ghost" size="icon" onClick={onRefresh} disabled={isFetching} aria-label="Refresh drafts">
            <RefreshCw className={isFetching ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
          </Button>
        </div>
        <Button className="w-full justify-between" onClick={onNew}>
          <span className="flex items-center gap-2"><Plus className="h-4 w-4" /> New generation run</span>
          <ArrowUpRight className="h-4 w-4 opacity-70" />
        </Button>
      </div>
      <div className="max-h-[430px] overflow-y-auto p-3 lg:max-h-none lg:flex-1">
        {runs.length === 0 ? (
          <div className="rounded-xl bg-slate-50 px-4 py-5 text-sm leading-6 text-slate-500">
            Saved drafts will appear here after the first run.
          </div>
        ) : (
          <div className="space-y-2">
            {runs.map((run) => (
              <button
                key={run.id}
                onClick={() => onSelect(run.id)}
                className={`group w-full rounded-xl border p-3 text-left transition ${
                  selectedId === run.id ? 'border-blue-200 bg-blue-50/70 shadow-sm' : 'border-transparent hover:border-slate-200 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="truncate text-sm font-semibold text-slate-900">{run.name}</span>
                  <ChevronRight className={`h-4 w-4 shrink-0 ${selectedId === run.id ? 'text-blue-700' : 'text-slate-300 group-hover:text-slate-500'}`} />
                </div>
                <div className="mt-2 flex items-center justify-between gap-2">
                  <span className="text-xs text-slate-500">{formatDate(run.createdAt)}</span>
                  <StatusBadge status={run.solverStatus} />
                </div>
                <div className="mt-3 flex gap-3 text-[11px] font-medium text-slate-500">
                  <span>{run.placementCount}/{run.offeringCount} placed</span>
                  <span className={run.conflictCount > 0 ? 'text-rose-600' : 'text-emerald-600'}>{run.conflictCount} conflicts</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="hidden border-t border-slate-200 p-5 lg:block">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-slate-600"><Database className="h-4 w-4" /></div>
          <div><p className="font-semibold text-slate-700">Versioned persistence</p><p>Drafts are saved to the scheduler database.</p></div>
        </div>
      </div>
    </aside>
  );
}

function SummaryStat({ icon: Icon, label, value, tone = 'slate' }: { icon: typeof Layers3; label: string; value: string | number; tone?: 'blue' | 'green' | 'amber' | 'slate' }) {
  const colors = { blue: 'bg-blue-50 text-blue-700', green: 'bg-emerald-50 text-emerald-700', amber: 'bg-amber-50 text-amber-700', slate: 'bg-slate-100 text-slate-600' };
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-2"><div className={`flex h-8 w-8 items-center justify-center rounded-lg ${colors[tone]}`}><Icon className="h-4 w-4" /></div><span className="text-2xl font-semibold tracking-tight text-slate-950">{value}</span></div>
      <p className="mt-3 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">{label}</p>
    </div>
  );
}

function ConflictList({ conflicts }: { conflicts: SolverConflict[] }) {
  if (conflicts.length === 0) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
        <CheckCircle2 className="h-5 w-5 shrink-0" />
        <div><p className="font-semibold">No conflicts detected</p><p className="mt-0.5 text-emerald-700">Every generated placement satisfies the current constraints.</p></div>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {conflicts.map((conflict, index) => (
        <div key={`${conflict.code}-${index}`} className="rounded-xl border border-rose-200 bg-rose-50/70 p-4">
          <div className="flex items-start gap-3"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" /><div className="min-w-0"><p className="text-sm font-semibold text-rose-900">{conflict.message}</p><p className="mt-1 text-xs font-medium uppercase tracking-[0.1em] text-rose-600">{conflict.code.replaceAll('_', ' ')}</p><p className="mt-2 text-xs text-rose-700">Offerings: {conflict.offeringIds.join(', ')}</p></div></div>
        </div>
      ))}
    </div>
  );
}

function PlacementTable({ detail }: { detail: TimetableRunDetail }) {
  const offerings = useMemo(() => new Map(detail.schedule.offerings.map((offering) => [offering.id, offering])), [detail.schedule.offerings]);
  const slots = useMemo(() => new Map(detail.schedule.timeSlots.map((slot) => [slot.id, slot])), [detail.schedule.timeSlots]);
  const rooms = useMemo(() => new Map(detail.schedule.rooms.map((room) => [room.id, room])), [detail.schedule.rooms]);
  const lecturers = useMemo(() => new Map(detail.schedule.lecturers.map((lecturer) => [lecturer.id, lecturer])), [detail.schedule.lecturers]);
  const sections = useMemo(() => new Map(detail.schedule.sections.map((section) => [section.id, section])), [detail.schedule.sections]);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200">
      <div className="grid grid-cols-[1.45fr_1fr_1fr_1fr] gap-4 border-b border-slate-200 bg-slate-50 px-4 py-3 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-400">
        <span>Offering</span><span>When</span><span>Room</span><span>Section / lecturer</span>
      </div>
      {detail.placements.length === 0 ? (
        <div className="p-6 text-center text-sm text-slate-500">No placements were returned for this run.</div>
      ) : (
        <div className="divide-y divide-slate-100">
          {detail.placements.map((placement) => {
            const offering = offerings.get(placement.offeringId);
            const slot = slots.get(placement.timeSlotId);
            const room = rooms.get(placement.roomId);
            const lecturer = offering ? lecturers.get(offering.lecturerId) : undefined;
            const section = offering ? sections.get(offering.sectionId) : undefined;
            return (
              <div key={placement.offeringId} className="grid grid-cols-[1.45fr_1fr_1fr_1fr] gap-4 px-4 py-4 text-sm">
                <div className="min-w-0"><p className="truncate font-semibold text-slate-900">{offering?.courseCode ?? placement.offeringId}</p><p className="mt-1 truncate text-xs text-slate-500">{offering?.courseName ?? 'Unknown offering'}</p></div>
                <div><p className="font-medium text-slate-800">{slot ? labelForDay(slot.day) : 'Unknown day'}</p><p className="mt-1 text-xs text-slate-500">{slot ? `${formatTime(slot.startMinute)} – ${formatTime(slot.endMinute)}` : 'Unknown time'}</p></div>
                <div><p className="font-medium text-slate-800">{room?.name ?? placement.roomId}</p><p className="mt-1 text-xs text-slate-500">{room ? `${room.type.toLowerCase()} · ${room.capacity} seats` : 'Unknown room'}</p></div>
                <div><p className="font-medium text-slate-800">{section?.name ?? offering?.sectionId ?? 'Unknown section'}</p><p className="mt-1 truncate text-xs text-slate-500">{lecturer?.name ?? offering?.lecturerId ?? 'Unknown lecturer'}</p></div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function RunDetail({ detail, onNew }: { detail: TimetableRunDetail; onNew: () => void }) {
  return (
    <main className="min-w-0 flex-1">
      <div className="mx-auto max-w-[1180px] px-5 py-7 sm:px-8 lg:px-10 lg:py-10">
        <div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-400"><span>Timetable review</span><span className="text-slate-300">/</span><span>Run {detail.id}</span></div>
            <div className="flex flex-wrap items-center gap-3"><h1 className="text-3xl font-semibold tracking-tight text-slate-950">{detail.name}</h1><StatusBadge status={detail.status} /><StatusBadge status={detail.solverStatus} /></div>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">{detail.message} Generated {formatDate(detail.createdAt)} from a saved scheduling input snapshot.</p>
          </div>
          <Button variant="outline" onClick={onNew}><Plus className="h-4 w-4" /> New version</Button>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <SummaryStat icon={Layers3} label="Offerings" value={detail.offeringCount} tone="blue" />
          <SummaryStat icon={CheckCircle2} label="Placements" value={detail.placementCount} tone="green" />
          <SummaryStat icon={AlertTriangle} label="Conflicts" value={detail.conflictCount} tone={detail.conflictCount ? 'amber' : 'green'} />
          <SummaryStat icon={Clock3} label="Solve time" value={`${detail.solveTimeMs}ms`} tone="slate" />
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader className="flex-row items-start justify-between gap-4"><div><CardTitle className="text-lg">Generated placements</CardTitle><p className="mt-1 text-sm text-slate-500">A reviewable allocation of courses, rooms, sections, and lecturers.</p></div><div className="hidden items-center gap-2 text-xs font-medium text-slate-500 sm:flex"><Cpu className="h-4 w-4 text-blue-600" /> Objective {detail.objectiveValue}</div></CardHeader>
            <CardContent><PlacementTable detail={detail} /></CardContent>
          </Card>

          <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
            <Card><CardHeader><CardTitle className="text-lg">Conflict review</CardTitle><p className="mt-1 text-sm text-slate-500">Constraint checks captured with this timetable version.</p></CardHeader><CardContent><ConflictList conflicts={detail.conflicts} /></CardContent></Card>
            <Card><CardHeader><CardTitle className="text-lg">Input snapshot</CardTitle><p className="mt-1 text-sm text-slate-500">The exact resources used by the solver for this run.</p></CardHeader><CardContent><div className="grid grid-cols-2 gap-3"><SummaryStat icon={Clock3} label="Time slots" value={detail.schedule.timeSlots.length} /><SummaryStat icon={DoorOpen} label="Rooms" value={detail.schedule.rooms.length} /><SummaryStat icon={Users} label="Lecturers" value={detail.schedule.lecturers.length} /><SummaryStat icon={FileJson} label="Sections" value={detail.schedule.sections.length} /></div><div className="mt-4 rounded-lg bg-slate-50 p-3 text-xs leading-5 text-slate-500"><span className="font-semibold text-slate-700">Solver window:</span> {detail.schedule.timeLimitSeconds ?? 120} seconds maximum</div></CardContent></Card>
          </div>
        </div>
      </div>
    </main>
  );
}

function GeneratorPanel({ onClose, onCreated }: { onClose: () => void; onCreated: (detail: TimetableRunDetail) => void }) {
  const [name, setName] = useState('CNCS timetable draft');
  const [json, setJson] = useState(starterJson);
  const [jsonError, setJsonError] = useState('');
  const createRun = useCreateTimetableRun();
  const queryClient = useQueryClient();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setJsonError('');
    let schedule: ScheduleGenerationRequest;
    try {
      schedule = JSON.parse(json) as ScheduleGenerationRequest;
    } catch {
      setJsonError('The scheduling data is not valid JSON. Check commas, quotes, and brackets.');
      return;
    }
    if (!schedule.timeSlots || !schedule.rooms || !schedule.lecturers || !schedule.sections || !schedule.offerings) {
      setJsonError('The JSON must include timeSlots, rooms, lecturers, sections, and offerings.');
      return;
    }
    createRun.mutate(
      { data: { name: name.trim() || 'Untitled timetable draft', schedule } },
      {
        onSuccess: (detail) => {
          queryClient.invalidateQueries({ queryKey: getListTimetableRunsQueryKey() });
          onCreated(detail);
        },
      },
    );
  }

  const errorMessage = createRun.error ? 'The solver could not save this draft. Check the scheduling data and try again.' : '';

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/35 p-0 backdrop-blur-[2px] sm:items-center sm:p-6">
      <div className="flex max-h-[94vh] w-full max-w-4xl flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl sm:rounded-2xl">
        <div className="flex items-start justify-between border-b border-slate-200 px-5 py-5 sm:px-7">
          <div><p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">New generation run</p><h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">Generate and save a timetable draft</h2><p className="mt-2 text-sm text-slate-500">The full input snapshot and solver result will be persisted as a new version.</p></div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close generator"><X className="h-5 w-5" /></Button>
        </div>
        <form onSubmit={handleSubmit} className="min-h-0 overflow-y-auto px-5 py-6 sm:px-7">
          <label className="block text-sm font-semibold text-slate-800" htmlFor="run-name">Draft name</label>
          <Input id="run-name" value={name} onChange={(event) => setName(event.target.value)} maxLength={120} className="mt-2 max-w-xl" placeholder="e.g. Week 1 timetable draft" />
          <div className="mt-6 flex items-end justify-between gap-4"><div><label className="text-sm font-semibold text-slate-800" htmlFor="schedule-json">Scheduling data</label><p className="mt-1 text-xs leading-5 text-slate-500">Edit the JSON snapshot to match your current rooms, lecturers, sections, offerings, and availability.</p></div><Button type="button" variant="outline" size="sm" onClick={() => { setJson(starterJson); setJsonError(''); }}>Load starter</Button></div>
          <Textarea id="schedule-json" value={json} onChange={(event) => setJson(event.target.value)} className="mt-2 min-h-[320px] resize-y bg-slate-950 font-mono text-xs leading-5 text-slate-100 placeholder:text-slate-500" spellCheck={false} />
          {jsonError || errorMessage ? <div className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{jsonError || errorMessage}</div> : null}
          <div className="mt-6 flex flex-col-reverse justify-end gap-3 border-t border-slate-200 pt-5 sm:flex-row"><Button type="button" variant="outline" onClick={onClose}>Cancel</Button><Button type="submit" disabled={createRun.isPending}>{createRun.isPending ? <><Loader2 className="h-4 w-4 animate-spin" /> Running solver…</> : <><Sparkles className="h-4 w-4" /> Generate and save draft</>}</Button></div>
        </form>
      </div>
    </div>
  );
}

function Workspace({ routeRunId }: { routeRunId?: string }) {
  const [, navigate] = useLocation();
  const [generatorOpen, setGeneratorOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(routeRunId ? Number(routeRunId) : null);
  const runsQuery = useListTimetableRuns();
  const runs = runsQuery.data ?? [];
  const effectiveId = routeRunId ? Number(routeRunId) : selectedId ?? runs[0]?.id ?? null;
  const detailQuery = useGetTimetableRun(effectiveId ?? 0, {
    query: {
      enabled: effectiveId !== null,
      queryKey: getGetTimetableRunQueryKey(effectiveId ?? 0),
    },
  });
  const detail = detailQuery.data;

  function selectRun(id: number) {
    setSelectedId(id);
    navigate(`/runs/${id}`);
  }

  function handleCreated(newDetail: TimetableRunDetail) {
    setGeneratorOpen(false);
    setSelectedId(newDetail.id);
    navigate(`/runs/${newDetail.id}`);
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb] text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="flex h-[72px] items-center justify-between px-5 sm:px-8 lg:px-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-700 text-white shadow-sm"><CalendarClock className="h-5 w-5" /></div>
            <div><p className="text-[11px] font-bold uppercase tracking-[0.2em] text-blue-700">SUTMS</p><p className="text-sm font-semibold text-slate-900">Scheduler workspace</p></div>
          </div>
          <div className="flex items-center gap-3"><div className="hidden items-center gap-2 text-xs font-medium text-slate-500 sm:flex"><CircleDashed className="h-3.5 w-3.5 text-emerald-500" /> OR-Tools engine ready</div><Button onClick={() => setGeneratorOpen(true)}><Plus className="h-4 w-4" /> New run</Button></div>
        </div>
      </header>
      <div className="flex min-h-[calc(100vh-72px)] flex-col lg:flex-row">
        <RunList runs={runs} selectedId={effectiveId} onSelect={selectRun} onNew={() => setGeneratorOpen(true)} onRefresh={() => runsQuery.refetch()} isFetching={runsQuery.isFetching} />
        {runsQuery.isLoading || (effectiveId !== null && detailQuery.isLoading) ? (
          <main className="flex flex-1 items-center justify-center p-8"><div className="flex items-center gap-3 text-sm text-slate-500"><Loader2 className="h-5 w-5 animate-spin text-blue-700" /> Loading timetable draft…</div></main>
        ) : runsQuery.isError || detailQuery.isError ? (
          <main className="flex flex-1 items-center justify-center p-8"><div className="max-w-md rounded-2xl border border-rose-200 bg-rose-50 p-6 text-center"><AlertTriangle className="mx-auto h-7 w-7 text-rose-600" /><h2 className="mt-3 font-semibold text-rose-900">Could not load this draft</h2><p className="mt-2 text-sm leading-6 text-rose-700">Refresh the workspace or choose another saved timetable version.</p><Button variant="outline" className="mt-4" onClick={() => { runsQuery.refetch(); if (effectiveId) detailQuery.refetch(); }}>Try again</Button></div></main>
        ) : detail ? <RunDetail detail={detail} onNew={() => setGeneratorOpen(true)} /> : <main className="flex-1 p-5 sm:p-8 lg:p-10"><EmptyState onNew={() => setGeneratorOpen(true)} /></main>}
      </div>
      {generatorOpen ? <GeneratorPanel onClose={() => setGeneratorOpen(false)} onCreated={handleCreated} /> : null}
    </div>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={() => <Workspace />} />
      <Route path="/runs/:id" component={({ params }: { params: { id: string } }) => <Workspace routeRunId={params.id} />} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
        <Router />
      </WouterRouter>
    </QueryClientProvider>
  );
}

export default App;