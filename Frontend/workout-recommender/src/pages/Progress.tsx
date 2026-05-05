import { useEffect, useMemo, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Target, TrendingUp, Zap } from 'lucide-react';
import { api } from '../lib/api';

type CheckInRow = {
  id: number;
  date: string;
  current_weight: number | null;
  workout_completed: boolean;
};

type HistoryResponse<T> = { count: number; results: T[] };

export default function Progress() {
  const [checkins, setCheckins] = useState<CheckInRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    api.checkInHistory()
      .then((data) => {
        const results = Array.isArray(data) ? data : (data as HistoryResponse<CheckInRow>).results;
        setCheckins([...results].reverse());
      })
      .catch((err) => setNotice(err instanceof Error ? err.message : "Unable to fetch progress data."))
      .finally(() => setIsLoading(false));
  }, []);

  const data = useMemo(() => checkins.map((row, index) => ({
    name: row.date || `Entry ${index + 1}`,
    weight: row.current_weight,
    setsCompleted: row.workout_completed ? 1 : 0,
    consistency: Math.round((checkins.slice(0, index + 1).filter((item) => item.workout_completed).length / (index + 1)) * 100),
  })), [checkins]);

  const weights = data.map((row) => row.weight).filter((weight): weight is number => typeof weight === "number");
  const latestWeight = weights.at(-1);
  const startWeight = weights[0];
  const completedWorkouts = checkins.filter((row) => row.workout_completed).length;
  const consistency = checkins.length ? Math.round((completedWorkouts / checkins.length) * 100) : 0;

  return (
    <div className="space-y-6 animate-content-reveal">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold">Progress Analytics</h2>
          <p className="text-muted-foreground mt-1">Track your consistency and metric improvements from backend check-ins.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8 stagger-children">
        <MetricCard icon={<TrendingUp />} label="Weight Log" value={`${latestWeight ?? '-'} kg`} note={latestWeight && startWeight ? `${(latestWeight - startWeight).toFixed(1)} kg from start` : "Add check-ins to track change"} />
        <MetricCard icon={<Target />} label="Workouts Logged" value={String(completedWorkouts)} note="Live from backend check-ins" accent="text-secondary" />
        <MetricCard icon={<Zap />} label="Consistency" value={`${consistency}%`} note={checkins.length ? `${completedWorkouts} of ${checkins.length} check-ins completed` : "No check-ins yet"} accent="text-accent" />
      </div>

      <div className="bg-card border border-border rounded-2xl shadow-card overflow-hidden">
        <div className="border-b border-border p-6 bg-muted/20">
          <h3 className="font-semibold text-lg">Weight Trajectory Vs Workout Completion</h3>
        </div>
        <div className="p-6 h-[400px]">
          {isLoading && <EmptyChart text="Fetching live progress..." />}
          {!isLoading && notice && <EmptyChart text={notice} />}
          {!isLoading && !notice && data.length === 0 && <EmptyChart text="Complete daily check-ins to build your progress chart." />}
          {!isLoading && !notice && data.length > 0 && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorWeight" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorSets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--secondary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--secondary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" tick={{ fill: 'hsl(var(--muted-foreground))' }} tickLine={false} axisLine={false} dy={10} />
                <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" tick={{ fill: 'hsl(var(--muted-foreground))' }} tickLine={false} axisLine={false} domain={['dataMin - 1', 'dataMax + 1']} />
                <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" tick={{ fill: 'hsl(var(--muted-foreground))' }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '12px', color: 'hsl(var(--foreground))' }} itemStyle={{ fontWeight: 500 }} />
                <Area yAxisId="left" type="monotone" dataKey="weight" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorWeight)" activeDot={{ r: 8, fill: 'hsl(var(--primary))' }} />
                <Area yAxisId="right" type="stepAfter" dataKey="setsCompleted" stroke="hsl(var(--secondary))" strokeWidth={3} fillOpacity={1} fill="url(#colorSets)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value, note, accent = "text-primary" }: { icon: React.ReactNode; label: string; value: string; note: string; accent?: string }) {
  return (
    <div className="bg-card border border-border p-6 rounded-2xl shadow-sm hover-lift">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 bg-muted/40 ${accent} rounded-xl flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider">{label}</p>
          <h3 className="text-2xl font-bold">{value}</h3>
        </div>
      </div>
      <div className={`mt-4 text-sm font-medium ${accent}`}>{note}</div>
    </div>
  );
}

function EmptyChart({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center text-muted-foreground">{text}</div>;
}
