import React, { useEffect, useState } from "react";
import { CalendarCheck, HeartPulse, Save, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { buildRecommendation, getCheckIn, getProfile, saveCheckIn, saveRecommendation } from "../lib/recommendationData";
import type { DailyCheckIn as CheckIn } from "../lib/recommendationData";
import { api } from "../lib/api";

const sleepOptions = [["poor", "Poor"], ["fair", "Fair"], ["good", "Good"]];
const intensityOptions = [["low", "Low"], ["moderate", "Moderate"], ["high", "High"]];

export default function DailyCheckIn() {
  const [checkin, setCheckin] = useState<CheckIn>(getCheckIn);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.latestCheckIn()
      .then((data) => {
        const next = { ...getCheckIn(), ...(data as Partial<CheckIn>) };
        setCheckin(next);
        saveCheckIn(next);
      })
      .catch(() => {
        setNotice("No backend check-in found yet. Today's readiness will be saved when you submit.");
      })
      .finally(() => setIsLoading(false));
  }, []);

  const set = (field: keyof CheckIn, value: string | number | boolean) => {
    setCheckin((current) => ({ ...current, [field]: value }));
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setNotice("");
    try {
      const saved = await api.saveCheckIn(checkin as unknown as Record<string, unknown>) as Partial<CheckIn>;
      const next = { ...checkin, ...saved };
      saveCheckIn(next);
      const generated = await api.generateRecommendation();
      saveRecommendation((generated.data ?? buildRecommendation(getProfile(), next)) as ReturnType<typeof buildRecommendation>);
      navigate("/plan");
    } catch (err) {
      saveCheckIn(checkin);
      saveRecommendation(buildRecommendation(getProfile(), checkin));
      setNotice(err instanceof Error ? `${err.message}. Showing locally adapted plan until the backend is reachable.` : "Backend save failed. Showing locally adapted plan.");
      navigate("/plan");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6 max-w-5xl animate-content-reveal">
      {(isLoading || notice) && (
        <div className="rounded-lg border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
          {isLoading ? "Loading your latest backend check-in..." : notice}
        </div>
      )}
      <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
        <div className="border-b border-border bg-muted/20 p-5 flex items-center justify-between">
          <h2 className="font-semibold flex items-center gap-2"><CalendarCheck /> Daily Readiness Check-In</h2>
          <span className="text-xs font-bold uppercase text-secondary">Context-aware adjustments</span>
        </div>
        <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <TextField type="date" label="Date" value={checkin.date} onChange={(v) => set("date", v)} />
          <NumberField label="Current Weight" suffix="KG" value={checkin.current_weight} onChange={(v) => set("current_weight", v)} />
          <SelectField label="Sleep Quality" value={checkin.sleep_quality} values={sleepOptions} onChange={(v) => set("sleep_quality", v)} />
          <NumberField label="Sleep Hours" value={checkin.sleep_hours} onChange={(v) => set("sleep_hours", v)} />
          <NumberField label="Daily Steps" value={checkin.daily_steps} onChange={(v) => set("daily_steps", v)} />
          <NumberField label="Resting Heart Rate" suffix="BPM" value={checkin.resting_heart_rate} onChange={(v) => set("resting_heart_rate", v)} />
          <NumberField label="Available Minutes" value={checkin.available_minutes} onChange={(v) => set("available_minutes", v)} />
          <SelectField label="Preferred Intensity" value={checkin.preferred_intensity} values={intensityOptions} onChange={(v) => set("preferred_intensity", v)} />
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-[1fr_0.85fr] gap-6">
        <div className="bg-card border border-border rounded-lg shadow-card p-5 space-y-5">
          <h3 className="font-semibold flex items-center gap-2"><HeartPulse /> Readiness Scores</h3>
          <Slider label="Energy" value={checkin.energy_level} low="Drained" high="Ready" onChange={(v) => set("energy_level", v)} />
          <Slider label="Soreness" value={checkin.soreness_level} low="Fresh" high="Very sore" onChange={(v) => set("soreness_level", v)} />
          <Slider label="Stress" value={checkin.stress_level} low="Calm" high="High" onChange={(v) => set("stress_level", v)} />
        </div>

        <div className="bg-card border border-border rounded-lg shadow-card p-5 space-y-4">
          <Toggle label="Workout Completed Today" checked={checkin.workout_completed} onChange={(v) => set("workout_completed", v)} />
          <Toggle label="Pain or Injury Present" checked={checkin.pain_or_injury} onChange={(v) => set("pain_or_injury", v)} />
          <TextField label="Injury Area" value={checkin.injury_area} placeholder="knee, shoulder, back..." onChange={(v) => set("injury_area", v)} />
          <label className="space-y-2 block text-sm">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Notes</span>
            <textarea value={checkin.notes} onChange={(e) => set("notes", e.target.value)} className="min-h-28 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-medium outline-none focus:ring-2 focus:ring-primary/50" />
          </label>
        </div>
      </section>

      <div className="flex justify-end gap-3">
        <button type="button" onClick={() => saveCheckIn(checkin)} className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-5 py-3 text-sm font-semibold hover:bg-muted">
          <Save size={18} /> Save Check-In
        </button>
        <button disabled={saving} className="inline-flex items-center gap-2 rounded-lg bg-gradient-hero px-6 py-3 text-sm font-semibold text-white shadow-elegant disabled:opacity-70">
          <Sparkles size={18} /> {saving ? "Adapting..." : "Adapt Today's Plan"}
        </button>
      </div>
    </form>
  );
}

function NumberField({ label, value, suffix, onChange }: { label: string; value: number | ""; suffix?: string; onChange: (v: number | "") => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><div className="relative"><input type="number" value={value} onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 pr-12 font-medium outline-none focus:ring-2 focus:ring-primary/50" />{suffix && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">{suffix}</span>}</div></label>;
}

function TextField({ label, value, type = "text", placeholder, onChange }: { label: string; value: string; type?: string; placeholder?: string; onChange: (v: string) => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><input type={type} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 font-medium outline-none focus:ring-2 focus:ring-primary/50" /></label>;
}

function SelectField({ label, value, values, onChange }: { label: string; value: string; values: string[][]; onChange: (v: string) => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><select value={value} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 pr-10 font-medium outline-none transition-all hover:border-primary/50 focus:ring-2 focus:ring-primary/50">{values.map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>;
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return <button type="button" onClick={() => onChange(!checked)} className={`flex w-full items-center justify-between rounded-lg border px-3 py-3 text-sm font-semibold ${checked ? "border-primary/60 bg-primary/10 text-primary" : "border-border bg-background text-muted-foreground"}`}><span>{label}</span><span className={`h-5 w-9 rounded-full p-0.5 ${checked ? "bg-primary" : "bg-muted"}`}><span className={`block h-4 w-4 rounded-full bg-white transition-transform ${checked ? "translate-x-4" : ""}`} /></span></button>;
}

function Slider({ label, value, low, high, onChange }: { label: string; value: number; low: string; high: string; onChange: (v: number) => void }) {
  return <label className="block space-y-2"><div className="flex items-center justify-between"><span className="text-sm font-semibold">{label}</span><span className="rounded-md bg-primary/10 px-2 py-0.5 text-sm font-bold text-primary">{value}/5</span></div><input type="range" min={1} max={5} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-primary" /><div className="flex justify-between text-xs text-muted-foreground"><span>{low}</span><span>{high}</span></div></label>;
}
