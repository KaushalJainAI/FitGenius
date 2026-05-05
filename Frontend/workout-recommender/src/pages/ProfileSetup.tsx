import React, { useEffect, useMemo, useState } from "react";
import { Activity, HeartPulse, Salad, Save, Sparkles, UserRound } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { bmi, bmiLabel, buildRecommendation, getCheckIn, getProfile, saveProfile, saveRecommendation } from "../lib/recommendationData";
import type { HealthProfile } from "../lib/recommendationData";
import { api } from "../lib/api";

const goals = [["weight_loss", "Weight Loss"], ["weight_gain", "Weight Gain"], ["muscle_gain", "Muscle Gain"], ["maintenance", "Maintenance"], ["endurance", "Endurance"]];
const options = {
  gender: [["male", "Male"], ["female", "Female"], ["other", "Other"]],
  activity: [["sedentary", "Sedentary"], ["low", "Low"], ["moderate", "Moderate"], ["active", "Active"], ["very_active", "Very Active"]],
  diet: [["no_preference", "No Preference"], ["vegetarian", "Vegetarian"], ["non_veg", "Non-Vegetarian"], ["vegan", "Vegan"], ["pescatarian", "Pescatarian"], ["keto", "Keto"], ["paleo", "Paleo"], ["mediterranean", "Mediterranean"]],
  sleep: [["poor", "Poor"], ["fair", "Fair"], ["good", "Good"]],
  alcohol: [["none", "None"], ["occasional", "Occasional"], ["regular", "Regular"]],
  risk: [["low", "Low"], ["moderate", "Moderate"], ["high", "High"]],
  experience: [["beginner", "Beginner"], ["intermediate", "Intermediate"], ["advanced", "Advanced"]],
  workout: [["mixed", "Mixed"], ["strength", "Strength"], ["cardio", "Cardio"], ["flexibility", "Flexibility"], ["hiit", "HIIT"]],
  equipment: [["full_gym", "Full Gym"], ["dumbbells", "Dumbbells"], ["bodyweight", "Bodyweight"], ["home_gym", "Home Gym"], ["resistance_bands", "Resistance Bands"]],
};

export default function ProfileSetup() {
  const [profile, setProfile] = useState<HealthProfile>(getProfile);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const navigate = useNavigate();
  const bmiValue = useMemo(() => bmi(profile), [profile]);

  useEffect(() => {
    api.profile()
      .then((data) => {
        const next = { ...getProfile(), ...(data as Partial<HealthProfile>) };
        setProfile(next);
        saveProfile(next);
      })
      .catch(() => {
        setNotice("No backend profile found yet. Fill this once and it will be saved to your account.");
      })
      .finally(() => setIsLoading(false));
  }, []);

  const set = (field: keyof HealthProfile, value: string | number | boolean) => {
    setProfile((current) => ({ ...current, [field]: value }));
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsGenerating(true);
    setNotice("");
    try {
      const saved = await api.saveProfile(profile as unknown as Record<string, unknown>) as Partial<HealthProfile>;
      const next = { ...profile, ...saved };
      saveProfile(next);
      const generated = await api.generateRecommendation();
      const recommendation = (generated.data ?? buildRecommendation(next, getCheckIn())) as ReturnType<typeof buildRecommendation>;
      saveRecommendation(recommendation);
      navigate("/plan");
    } catch (err) {
      saveProfile(profile);
      saveRecommendation(buildRecommendation(profile, getCheckIn()));
      setNotice(err instanceof Error ? `${err.message}. Showing locally generated plan until the backend is reachable.` : "Backend save failed. Showing locally generated plan.");
      navigate("/plan");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6 animate-content-reveal">
      {(isLoading || notice) && (
        <div className="rounded-lg border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
          {isLoading ? "Loading your backend profile..." : notice}
        </div>
      )}
      <div className="grid grid-cols-1 xl:grid-cols-[1.15fr_0.85fr] gap-6">
        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <SectionTitle icon={<UserRound />} title="Body Profile" action={`${bmiValue} ${bmiLabel(bmiValue)}`} />
          <div className="p-5 grid grid-cols-1 md:grid-cols-4 gap-4">
            <NumberField label="Age" value={profile.age} onChange={(v) => set("age", v)} />
            <SelectField label="Gender" value={profile.gender} values={options.gender} onChange={(v) => set("gender", v)} />
            <NumberField label="Height" suffix="CM" value={profile.height} onChange={(v) => set("height", v)} />
            <NumberField label="Weight" suffix="KG" value={profile.weight} onChange={(v) => set("weight", v)} />
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <SectionTitle icon={<Activity />} title="Training Fit" action={`${profile.exercise_frequency} days/week`} />
          <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SelectField label="Goal" value={profile.fitness_goal} values={goals} onChange={(v) => set("fitness_goal", v)} />
            <SelectField label="Experience" value={profile.experience_level} values={options.experience} onChange={(v) => set("experience_level", v)} />
            <SelectField label="Workout Type" value={profile.preferred_workout_type} values={options.workout} onChange={(v) => set("preferred_workout_type", v)} />
            <SelectField label="Equipment" value={profile.available_equipment} values={options.equipment} onChange={(v) => set("available_equipment", v)} />
            <NumberField label="Days per week" value={profile.exercise_frequency} min={1} max={7} onChange={(v) => set("exercise_frequency", v)} />
            <SelectField label="Activity Level" value={profile.activity_level} values={options.activity} onChange={(v) => set("activity_level", v)} />
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <SectionTitle icon={<HeartPulse />} title="Medical & Lifestyle Signals" action="Safety rules" />
          <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <TextField label="Chronic Disease" value={profile.chronic_disease} placeholder="None, heart disease..." onChange={(v) => set("chronic_disease", v)} />
            <NumberField label="Systolic BP" value={profile.blood_pressure_systolic} onChange={(v) => set("blood_pressure_systolic", v)} />
            <NumberField label="Diastolic BP" value={profile.blood_pressure_diastolic} onChange={(v) => set("blood_pressure_diastolic", v)} />
            <NumberField label="Cholesterol" suffix="mg/dL" value={profile.cholesterol} onChange={(v) => set("cholesterol", v)} />
            <SelectField label="Genetic Risk" value={profile.genetic_risk} values={options.risk} onChange={(v) => set("genetic_risk", v)} />
            <SelectField label="Sleep Quality" value={profile.sleep_quality} values={options.sleep} onChange={(v) => set("sleep_quality", v)} />
            <Toggle label="Hypertension" checked={profile.hypertension} onChange={(v) => set("hypertension", v)} />
            <Toggle label="Diabetes" checked={profile.diabetes} onChange={(v) => set("diabetes", v)} />
            <Toggle label="Smoking Habit" checked={profile.smoking_habit} onChange={(v) => set("smoking_habit", v)} />
            <SelectField label="Alcohol" value={profile.alcohol_consumption} values={options.alcohol} onChange={(v) => set("alcohol_consumption", v)} />
            <NumberField label="Daily Steps" value={profile.daily_steps} onChange={(v) => set("daily_steps", v)} />
            <NumberField label="Avg Heart Rate" suffix="BPM" value={profile.avg_heart_rate} onChange={(v) => set("avg_heart_rate", v)} />
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <SectionTitle icon={<Salad />} title="Nutrition Inputs" action="Diet templates" />
          <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SelectField label="Dietary Preference" value={profile.dietary_preference} values={options.diet} onChange={(v) => set("dietary_preference", v)} />
            <TextField label="Cuisine Preference" value={profile.cuisine_preference} placeholder="Indian, Mediterranean..." onChange={(v) => set("cuisine_preference", v)} />
            <NumberField label="Current Calories" value={profile.caloric_intake} onChange={(v) => set("caloric_intake", v)} />
            <NumberField label="Protein" suffix="G" value={profile.protein_intake} onChange={(v) => set("protein_intake", v)} />
            <NumberField label="Carbs" suffix="G" value={profile.carbohydrate_intake} onChange={(v) => set("carbohydrate_intake", v)} />
            <NumberField label="Fat" suffix="G" value={profile.fat_intake} onChange={(v) => set("fat_intake", v)} />
            <div className="sm:col-span-2">
              <TextField label="Food Aversions" value={profile.food_aversion} placeholder="Foods to avoid" onChange={(v) => set("food_aversion", v)} />
            </div>
          </div>
        </section>
      </div>

      <div className="flex justify-end gap-3">
        <button type="button" onClick={() => { saveProfile(profile); }} className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-5 py-3 text-sm font-semibold hover:bg-muted">
          <Save size={18} /> Save Profile
        </button>
        <button disabled={isGenerating} className="inline-flex items-center gap-2 rounded-lg bg-gradient-hero px-6 py-3 text-sm font-semibold text-white shadow-elegant disabled:opacity-70">
          <Sparkles size={18} /> {isGenerating ? "Generating..." : "Generate Plan"}
        </button>
      </div>
    </form>
  );
}

function SectionTitle({ icon, title, action }: { icon: React.ReactNode; title: string; action: string }) {
  return <div className="border-b border-border bg-muted/20 p-5 flex items-center justify-between"><h2 className="font-semibold flex items-center gap-2">{icon}{title}</h2><span className="text-xs font-bold uppercase text-secondary">{action}</span></div>;
}

function NumberField({ label, value, suffix, min, max, onChange }: { label: string; value: number | ""; suffix?: string; min?: number; max?: number; onChange: (v: number | "") => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><div className="relative"><input type="number" min={min} max={max} value={value} onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 pr-12 font-medium outline-none focus:ring-2 focus:ring-primary/50" />{suffix && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">{suffix}</span>}</div></label>;
}

function TextField({ label, value, placeholder, onChange }: { label: string; value: string; placeholder?: string; onChange: (v: string) => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><input value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 font-medium outline-none focus:ring-2 focus:ring-primary/50" /></label>;
}

function SelectField({ label, value, values, onChange }: { label: string; value: string; values: string[][]; onChange: (v: string) => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><select value={value} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 pr-10 font-medium outline-none transition-all hover:border-primary/50 focus:ring-2 focus:ring-primary/50">{values.map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>;
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return <button type="button" onClick={() => onChange(!checked)} className={`flex h-[42px] items-center justify-between self-end rounded-lg border px-3 text-sm font-semibold ${checked ? "border-primary/60 bg-primary/10 text-primary" : "border-border bg-background text-muted-foreground"}`}><span>{label}</span><span className={`h-5 w-9 rounded-full p-0.5 ${checked ? "bg-primary" : "bg-muted"}`}><span className={`block h-4 w-4 rounded-full bg-white transition-transform ${checked ? "translate-x-4" : ""}`} /></span></button>;
}
