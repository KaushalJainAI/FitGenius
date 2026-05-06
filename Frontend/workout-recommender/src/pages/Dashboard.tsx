import { ArrowRight, Activity, Calendar, Award, HeartPulse } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { bmi, bmiLabel, defaultCheckIn, defaultProfile } from "../lib/recommendationData";
import type { DailyCheckIn, HealthProfile, Recommendation } from "../lib/recommendationData";
import { api } from "../lib/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [checkin, setCheckin] = useState<DailyCheckIn | null>(null);
  const [plan, setPlan] = useState<Recommendation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.dashboardSummary()
      .then((data) => {
        const summary = data as {
          profile?: Partial<HealthProfile> | null;
          latest_checkin?: Partial<DailyCheckIn> | null;
          latest_recommendation?: Recommendation | null;
        };
        if (summary.profile) setProfile({ ...defaultProfile, ...summary.profile });
        if (summary.latest_checkin) setCheckin({ ...defaultCheckIn, ...summary.latest_checkin });
        if (summary.latest_recommendation) setPlan(summary.latest_recommendation);
      })
      .catch(() => {
        Promise.allSettled([
          api.profile(),
          api.latestCheckIn(),
          api.latestRecommendation(),
        ]).then(([profileResult, checkinResult, planResult]) => {
          if (profileResult.status === "fulfilled") setProfile({ ...defaultProfile, ...(profileResult.value as Partial<HealthProfile>) });
          if (checkinResult.status === "fulfilled") setCheckin({ ...defaultCheckIn, ...(checkinResult.value as Partial<DailyCheckIn>) });
          if (planResult.status === "fulfilled") setPlan(planResult.value as Recommendation);
        });
      })
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="rounded-lg border border-border bg-card p-6 text-muted-foreground">Fetching your live dashboard from the backend...</div>;
  }

  if (!profile) {
    return (
      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-xl font-bold">Create your health profile first</h2>
        <p className="mt-2 text-muted-foreground">Your dashboard is locked to backend data, so it needs an authenticated profile before showing recommendations.</p>
        <button onClick={() => navigate("/profile")} className="mt-5 rounded-lg bg-primary px-5 py-2.5 font-medium text-primary-foreground hover:bg-primary/90">Set up profile</button>
      </div>
    );
  }

  const liveCheckin = checkin ?? defaultCheckIn;
  const bmiValue = bmi(profile);

  return (
    <div className="space-y-6 stagger-children animate-fade-in-up">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard icon={<Activity />} label="Current Split" value={plan?.workout_split ?? "No plan yet"} />
        <StatCard icon={<Calendar />} label="Training Days" value={`${profile.exercise_frequency}/week`} />
        <StatCard icon={<Award />} label="BMI Status" value={`${bmiValue} ${bmiLabel(bmiValue)}`} />
        <StatCard icon={<HeartPulse />} label="Readiness" value={checkin ? `${checkin.energy_level}/5 energy` : "No check-in"} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6 h-full">
        <div className="bg-card border border-border p-6 rounded-lg shadow-card hover-lift flex flex-col justify-between min-h-[300px]">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-secondary mb-3">Next workout</p>
            <h2 className="text-xl font-bold mb-2 text-foreground">{plan ? `${plan.exercise_plan[0]?.day}: ${plan.exercise_plan[0]?.focus}` : "Generate your first backend plan"}</h2>
            <p className="text-muted-foreground max-w-xl">
              Your plan is using {profile.fitness_goal.replace("_", " ")} goals, {profile.available_equipment.replace("_", " ")} access, and today's sleep, soreness, stress, injury, and time signals.
            </p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={() => navigate("/plan")} className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-2.5 rounded-lg font-medium transition-all hover:gap-3">
              View Plan <ArrowRight size={18} />
            </button>
            <button onClick={() => navigate("/check-in")} className="border border-border bg-background hover:bg-muted px-5 py-2.5 rounded-lg font-medium transition-colors">
              Daily Check-In
            </button>
          </div>
        </div>

        <div className="bg-card border border-border p-6 rounded-lg shadow-card min-h-[300px]">
          <h3 className="text-xl font-bold mb-2">Recommendation Pipeline Inputs</h3>
          <p className="text-muted-foreground text-sm mb-6">These are the fields currently shaping your workout, diet, medical safety rules, and daily context adjustments.</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <Signal label="Goal" value={profile.fitness_goal.replace("_", " ")} />
            <Signal label="Experience" value={profile.experience_level} />
            <Signal label="Diet" value={profile.dietary_preference.replace("_", " ")} />
            <Signal label="Sleep" value={`${liveCheckin.sleep_hours || "-"}h / ${liveCheckin.sleep_quality}`} />
            <Signal label="Soreness" value={`${liveCheckin.soreness_level}/5`} />
            <Signal label="Stress" value={`${liveCheckin.stress_level}/5`} />
            <Signal label="Minutes" value={`${liveCheckin.available_minutes || 60}`} />
            <Signal label="Intensity" value={liveCheckin.preferred_intensity} />
          </div>
          <button onClick={() => navigate("/profile")} className="mt-6 w-full border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground px-5 py-2.5 rounded-lg font-medium transition-colors">
            Update Full Profile
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-card border border-border p-5 rounded-lg shadow-sm flex items-center gap-4 hover-lift">
      <div className="w-12 h-12 bg-muted/50 rounded-lg flex items-center justify-center text-primary border border-primary/10">{icon}</div>
      <div className="min-w-0">
        <p className="text-sm text-muted-foreground font-medium">{label}</p>
        <h3 className="text-xl font-bold text-foreground tracking-tight truncate">{value}</h3>
      </div>
    </div>
  );
}

function Signal({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-border bg-background p-3"><p className="text-xs font-bold uppercase text-muted-foreground">{label}</p><p className="mt-1 font-semibold capitalize">{value}</p></div>;
}
