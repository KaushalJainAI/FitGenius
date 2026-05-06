import React, { useEffect, useMemo, useState } from "react";
import { Activity, HeartPulse, Salad, Save, Sparkles, UserRound, Plus, Minus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { bmi, bmiLabel, defaultProfile, getProfile, saveProfile } from "../lib/recommendationData";
import type { HealthProfile } from "../lib/recommendationData";
import { api } from "../lib/api";
import { useTheme } from "../contexts/ThemeContext";
import { displayHeight, displayWeight, heightUnit, inputHeight, inputWeight, weightUnit } from "../lib/units";
import { Select } from "../components/Select";

type Choice = { value: string; label: string };
type ProfileOptions = typeof fallbackOptions & { chronicDisease: string[][] };

const fallbackGoals = [["weight_loss", "Weight Loss"], ["weight_gain", "Weight Gain"], ["maintenance", "Maintenance"]];
const fallbackOptions = {
  gender: [["male", "Male"], ["female", "Female"], ["other", "Other"]],
  activity: [["sedentary", "Sedentary"], ["moderate", "Moderate"], ["active", "Active"]],
  diet: [["no_preference", "No Preference"], ["regular", "Regular"], ["vegetarian", "Vegetarian"], ["vegan", "Vegan"], ["keto", "Keto"], ["low_sodium", "Low Sodium"], ["low_sugar", "Low Sugar"]],
  sleep: [["poor", "Poor"], ["fair", "Fair"], ["good", "Good"]],
  alcohol: [["none", "None"], ["occasional", "Occasional"], ["regular", "Regular"]],
  risk: [["low", "Low"], ["moderate", "Moderate"], ["high", "High"]],
  experience: [["beginner", "Beginner"], ["intermediate", "Intermediate"], ["advanced", "Advanced"]],
  workout: [["mixed", "Mixed"], ["strength", "Strength"], ["cardio", "Cardio"], ["flexibility", "Flexibility"], ["hiit", "HIIT"]],
  equipment: [["full_gym", "Full Gym"], ["dumbbells", "Dumbbells"], ["bodyweight", "Bodyweight"], ["home_gym", "Home Gym"], ["resistance_bands", "Resistance Bands"]],
  chronicDisease: [["", "None"], ["diabetes", "Diabetes"], ["heart_disease", "Heart Disease"], ["hypertension", "Hypertension"], ["obesity", "Obesity"]],
};

export default function ProfileSetup() {
  const [profile, setProfile] = useState<HealthProfile>(getProfile);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const [goals, setGoals] = useState<string[][]>(fallbackGoals);
  const [options, setOptions] = useState<ProfileOptions>(fallbackOptions);
  const navigate = useNavigate();
  const { measurementSystem } = useTheme();
  const bmiValue = useMemo(() => bmi(profile), [profile]);

  useEffect(() => {
    api.profileOptions()
      .then((data) => {
        const datasetOptions = data as Record<string, Choice[]>;
        setGoals(toPairs(datasetOptions.fitness_goal, fallbackGoals));
        setOptions((current) => ({
          ...current,
          gender: toPairs(datasetOptions.gender, current.gender),
          activity: toPairs(datasetOptions.activity_level, current.activity),
          diet: toPairs(datasetOptions.dietary_preference, current.diet),
          sleep: toPairs(datasetOptions.sleep_quality, current.sleep),
          alcohol: toPairs(datasetOptions.alcohol_consumption, current.alcohol),
          risk: toPairs(datasetOptions.genetic_risk, current.risk),
          experience: toPairs(datasetOptions.experience_level, current.experience),
          workout: toPairs(datasetOptions.preferred_workout_type, current.workout),
          equipment: toPairs(datasetOptions.available_equipment, current.equipment),
          chronicDisease: toPairs(datasetOptions.chronic_disease, current.chronicDisease),
        }));
      })
      .catch(() => {});
    api.profile()
      .then((data) => {
        const next = { ...defaultProfile, ...(data as Partial<HealthProfile>) };
        setProfile(next);
        saveProfile(next);
      })
      .catch(() => {
        api.profileDefaults()
          .then((defaults) => setProfile({ ...defaultProfile, ...(defaults as Partial<HealthProfile>) }))
          .catch(() => {});
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
      if (!generated.data) throw new Error("Backend did not return a recommendation.");
      navigate("/plan");
    } catch (err) {
      saveProfile(profile);
      setNotice(err instanceof Error ? err.message : "Backend save failed. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6 animate-content-reveal">
      {(isLoading || notice) && (
        <div className="rounded-lg border border-border bg-card px-4 py-3 text-sm text-muted-foreground whitespace-pre-line">
          {isLoading ? "Loading your backend profile..." : notice}
        </div>
      )}
      <div className="grid grid-cols-1 xl:grid-cols-[1.15fr_0.85fr] gap-6">
        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <SectionTitle icon={<UserRound />} title="Body Profile" action={`${bmiValue} ${bmiLabel(bmiValue)}`} />
          <div className="p-5 grid grid-cols-1 md:grid-cols-4 gap-4">
            <NumberField label="Age" value={profile.age} onChange={(v) => set("age", v)} />
            <SelectField label="Gender" value={profile.gender} values={options.gender} onChange={(v) => set("gender", v)} />
            <NumberField label="Height" suffix={heightUnit(measurementSystem)} value={displayHeight(profile.height, measurementSystem)} onChange={(v) => set("height", inputHeight(v, measurementSystem))} />
            <NumberField label="Weight" suffix={weightUnit(measurementSystem)} value={displayWeight(profile.weight, measurementSystem)} onChange={(v) => set("weight", inputWeight(v, measurementSystem))} />
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
            <SelectField label="Chronic Disease" value={normalizeChronicDisease(profile.chronic_disease)} values={options.chronicDisease} onChange={(v) => set("chronic_disease", v)} />
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

      <div className="sticky bottom-0 z-20 -mx-6 md:-mx-10 border-t border-border bg-background/90 px-6 py-4 backdrop-blur md:px-10">
        <div className="flex justify-end gap-3">
        <button type="button" onClick={async () => {
          setNotice("");
          setIsSaving(true);
          try {
            const saved = await api.saveProfile(profile as unknown as Record<string, unknown>) as Partial<HealthProfile>;
            const next = { ...profile, ...saved };
            setProfile(next);
            saveProfile(next);
            setNotice("Profile saved to the backend.");
          } catch (err) {
            setNotice(err instanceof Error ? err.message : "Backend save failed. Please try again.");
          } finally {
            setIsSaving(false);
          }
        }} disabled={isSaving || isGenerating} className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-5 py-3 text-sm font-semibold hover:bg-muted disabled:opacity-70">
          <Save size={18} /> {isSaving ? "Saving..." : "Save Profile"}
        </button>
        <button disabled={isGenerating} className="inline-flex items-center gap-2 rounded-lg bg-gradient-hero px-6 py-3 text-sm font-semibold text-white shadow-elegant disabled:opacity-70">
          {isGenerating ? <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" /> : <Sparkles size={18} />} {isGenerating ? "Generating Plan..." : "Generate Plan"}
        </button>
        </div>
      </div>
    </form>
  );
}

function SectionTitle({ icon, title, action }: { icon: React.ReactNode; title: string; action: string }) {
  return <div className="border-b border-border bg-muted/20 p-5 flex items-center justify-between"><h2 className="font-semibold flex items-center gap-2">{icon}{title}</h2><span className="text-xs font-bold uppercase text-secondary">{action}</span></div>;
}

function NumberField({ label, value, suffix, min, max, onChange }: { label: string; value: number | "" | null; suffix?: string; min?: number; max?: number; onChange: (v: number | "") => void }) {
  const handleStep = (step: number) => {
    const current = Number(value) || 0;
    const next = current + step;
    if (min !== undefined && next < min) return;
    if (max !== undefined && next > max) return;
    onChange(next);
  };

  return (
    <label className="space-y-2 text-sm group">
      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">{label}</span>
      <div className="relative flex items-center h-[42px]">
        <button 
          type="button"
          onClick={() => handleStep(-1)}
          className="absolute left-1 z-10 p-1.5 rounded-md hover:bg-muted text-muted-foreground transition-colors active:scale-90"
        >
          <Minus size={14} />
        </button>
        <div className="relative w-full flex items-center justify-center h-full border border-border bg-background rounded-lg hover:border-primary/50 transition-all focus-within:ring-2 focus-within:ring-primary/50 overflow-hidden">
          <input 
            type="number" 
            min={min} 
            max={max} 
            value={value ?? ""} 
            onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))} 
            className="w-full h-full bg-transparent text-center text-foreground font-bold outline-none px-12" 
          />
          {suffix && (
            <span className="absolute right-8 top-1/2 -translate-y-1/2 text-[9px] font-black uppercase tracking-widest text-muted-foreground/30 pointer-events-none select-none">
              {suffix}
            </span>
          )}
        </div>
        <button 
          type="button"
          onClick={() => handleStep(1)}
          className="absolute right-1 z-10 p-1.5 rounded-md hover:bg-muted text-muted-foreground transition-colors active:scale-90"
        >
          <Plus size={14} />
        </button>
      </div>
    </label>
  );
}

function TextField({ label, value, placeholder, onChange }: { label: string; value: string; placeholder?: string; onChange: (v: string) => void }) {
  return <label className="space-y-2 text-sm"><span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span><input value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-foreground placeholder:text-muted-foreground/60 font-medium outline-none focus:ring-2 focus:ring-primary/50" /></label>;
}

function SelectField({ label, value, values, onChange }: { label: string; value: string; values: string[][]; onChange: (v: string) => void }) {
  const options = values.map(([val, lbl]) => ({ value: val, label: lbl }));
  return (
    <label className="space-y-2 text-sm group">
      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">{label}</span>
      <Select 
        options={options}
        value={value}
        onChange={onChange}
      />
    </label>
  );
}

function toPairs(values: Choice[] | undefined, fallback: string[][]) {
  return values?.length ? values.map((option) => [option.value, option.label]) : fallback;
}

function normalizeChronicDisease(value: string) {
  const normalized = value.trim().toLowerCase().replace(/\s+/g, "_");
  if (normalized === "none") return "";
  return normalized;
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button 
      type="button" 
      onClick={() => onChange(!checked)} 
      className={`flex w-full h-[42px] items-center justify-between self-end rounded-lg border px-4 gap-3 text-sm font-semibold transition-colors ${checked ? "border-primary/60 bg-primary/10 text-primary" : "border-border bg-background text-muted-foreground hover:bg-muted/50"}`}
    >
      <span className="truncate flex-1 text-left">{label}</span>
      <span className={`shrink-0 h-5 w-9 rounded-full p-0.5 transition-colors ${checked ? "bg-primary" : "bg-muted"}`}>
        <span className={`block h-4 w-4 rounded-full bg-white shadow-sm transition-transform ${checked ? "translate-x-4" : ""}`} />
      </span>
    </button>
  );
}
