import { ArrowRight, Activity, Calendar, Award, HeartPulse } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { bmi, bmiLabel, getCheckIn, getProfile, getRecommendation, saveCheckIn, saveProfile, saveRecommendation } from "../lib/recommendationData";
import { api } from "../lib/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(getProfile);
  const [checkin, setCheckin] = useState(getCheckIn);
  const [plan, setPlan] = useState(getRecommendation);
  const bmiValue = bmi(profile);

  useEffect(() => {
    api.profile().then((data) => {
      const next = { ...getProfile(), ...(data as object) };
      setProfile(next);
      saveProfile(next);
    }).catch(() => undefined);

    api.latestCheckIn().then((data) => {
      const next = { ...getCheckIn(), ...(data as object) };
      setCheckin(next);
      saveCheckIn(next);
    }).catch(() => undefined);

    api.latestRecommendation().then((data) => {
      const next = data as ReturnType<typeof getRecommendation>;
      setPlan(next);
      saveRecommendation(next);
    }).catch(() => undefined);
  }, []);

  return (
    <div className="space-y-6 stagger-children animate-fade-in-up">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard icon={<Activity />} label="Current Split" value={plan.workout_split} />
        <StatCard icon={<Calendar />} label="Training Days" value={`${profile.exercise_frequency}/week`} />
        <StatCard icon={<Award />} label="BMI Status" value={`${bmiValue} ${bmiLabel(bmiValue)}`} />
        <StatCard icon={<HeartPulse />} label="Readiness" value={`${checkin.energy_level}/5 energy`} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6 h-full">
        <div className="bg-card border border-border p-6 rounded-lg shadow-card hover-lift flex flex-col justify-between min-h-[300px]">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-secondary mb-3">Next workout</p>
            <h2 className="text-xl font-bold mb-2 text-foreground">{plan.exercise_plan[0]?.day}: {plan.exercise_plan[0]?.focus}</h2>
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
            <Signal label="Sleep" value={`${checkin.sleep_hours || "-"}h / ${checkin.sleep_quality}`} />
            <Signal label="Soreness" value={`${checkin.soreness_level}/5`} />
            <Signal label="Stress" value={`${checkin.stress_level}/5`} />
            <Signal label="Minutes" value={`${checkin.available_minutes || 60}`} />
            <Signal label="Intensity" value={checkin.preferred_intensity} />
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
