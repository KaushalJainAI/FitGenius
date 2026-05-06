import { CheckCircle, RefreshCw, Settings, Utensils } from "lucide-react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import type { Recommendation } from "../lib/recommendationData";
import { api } from "../lib/api";

export default function MyPlan() {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [notice, setNotice] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    api.latestRecommendation()
      .then((data) => setRecommendation(data as Recommendation))
      .catch((err) => setNotice(err instanceof Error ? err.message : "No backend plan found."))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="rounded-lg border border-border bg-card p-6 text-muted-foreground">Fetching your latest plan from the backend...</div>;
  }

  if (!recommendation) {
    return (
      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-xl font-bold">No backend plan yet</h2>
        <p className="mt-2 text-muted-foreground">{notice || "Generate a plan after completing your profile."}</p>
        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            disabled={isGenerating}
            onClick={async () => {
              setIsGenerating(true);
              setNotice("");
              try {
                await api.profile();
                const generated = await api.generateRecommendation();
                setRecommendation((generated.data ?? generated) as Recommendation);
              } catch (err) {
                setNotice(err instanceof Error ? err.message : "Complete your profile before generating a plan.");
              } finally {
                setIsGenerating(false);
              }
            }}
            className="inline-flex rounded-lg bg-primary px-5 py-2.5 font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-70"
          >
            {isGenerating ? "Generating..." : "Generate plan"}
          </button>
          <Link to="/profile" className="inline-flex rounded-lg border border-border bg-card px-5 py-2.5 font-medium hover:bg-muted">Edit profile</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6 animate-slide-in-right">
      <section className="bg-card border border-border overflow-hidden rounded-lg shadow-card flex flex-col min-h-[70vh]">
        {notice && <div className="border-b border-border bg-muted/20 px-6 py-3 text-sm text-muted-foreground">{notice}</div>}
        <div className="border-b border-border p-6 bg-muted/30 flex justify-between items-center gap-4">
          <div>
            <h2 className="font-semibold text-xl uppercase flex gap-2 items-center">
              {recommendation.workout_split} ({recommendation.workout_days_per_week} days/week)
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {recommendation.algorithm_used} model • {recommendation.similar_profiles_count} similar profiles • {recommendation.avg_similarity_score == null ? "N/A" : `${Math.round(recommendation.avg_similarity_score * 100)}%`} match
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex bg-secondary/10 text-secondary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-secondary/20 items-center justify-center">
              <CheckCircle size={14} className="mr-1 inline" /> {recommendation.confidence} Confidence
            </div>
            <Link to="/profile" className="h-10 w-10 flex items-center justify-center rounded-lg bg-muted/50 text-foreground hover:bg-muted transition-colors border border-border" title="Edit profile">
              <Settings className="h-5 w-5" />
            </Link>
          </div>
        </div>

        <div className="p-6 space-y-6 flex-1 overflow-y-auto">
          {recommendation.exercise_plan.map((day, index) => (
            <WorkoutDay key={day.day} day={day.day} focus={day.focus} colorClass={["text-primary", "text-accent", "text-secondary"][index % 3]} exercises={day.exercises} />
          ))}

          <div className="border-l-2 border-primary pl-4 py-3 bg-primary/5 rounded-e-lg border-y border-r border-border">
            <p className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
              <RefreshCw className="h-5 w-5 text-primary shrink-0 mt-0.5" />
              <span><strong className="text-foreground">Pipeline Explanation:</strong> {recommendation.explanation}</span>
            </p>
          </div>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="bg-card border border-border rounded-lg shadow-card overflow-hidden">
          <div className="border-b border-border bg-muted/20 p-5">
            <h3 className="font-semibold flex items-center gap-2"><Utensils /> Nutrition Target</h3>
          </div>
          <div className="p-5 space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Daily Calories</p>
              <p className="text-3xl font-bold">{recommendation.daily_calorie_target}</p>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <Macro label="Protein" value={recommendation.macro_split.protein_g} />
              <Macro label="Carbs" value={recommendation.macro_split.carbs_g} />
              <Macro label="Fat" value={recommendation.macro_split.fat_g} />
            </div>
            {Object.entries(recommendation.diet_plan).map(([meal, text]) => (
              <div key={meal} className="rounded-lg border border-border bg-background p-3">
                <p className="text-xs font-bold uppercase text-secondary">{meal}</p>
                <p className="text-sm mt-1 text-muted-foreground">{text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg shadow-card p-5 space-y-3">
          <h3 className="font-semibold">AI Coach Notes</h3>
          <p className="text-sm text-muted-foreground whitespace-pre-line">{recommendation.llm_recommendation}</p>
          <div className="rounded-lg border border-border bg-background p-3 text-sm text-muted-foreground whitespace-pre-line">{recommendation.health_notes}</div>
          <Link to="/check-in" className="inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90">
            Update Today's Readiness
          </Link>
        </section>
      </aside>
    </div>
  );
}

function Macro({ label, value }: { label: string; value: number }) {
  return <div className="rounded-lg bg-muted/30 p-3 text-center"><p className="text-lg font-bold">{value}g</p><p className="text-xs text-muted-foreground">{label}</p></div>;
}

type Exercise = Recommendation["exercise_plan"][number]["exercises"][number];

function WorkoutDay({ day, focus, colorClass, exercises }: { day: string; focus: string; colorClass: string; exercises: Exercise[] }) {
  return (
    <div className="border border-border/60 rounded-lg overflow-hidden hover-lift bg-background shadow-sm transition-all group">
      <div className="px-5 py-4 flex items-center gap-2 border-b border-border/60 bg-muted/20 group-hover:bg-muted/40 transition-colors">
        <h4 className="font-semibold flex flex-wrap items-center gap-2 text-foreground">
          <span className="bg-background px-2 py-0.5 rounded shadow-sm border border-border text-sm"><span className={colorClass}>{day}</span></span>
          <span className="text-muted-foreground">/</span>
          <span>Focus: {focus}</span>
        </h4>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-background hidden sm:table-header-group">
            <tr>
              <th className="text-left py-3 px-5 font-semibold text-muted-foreground w-1/3 text-xs uppercase tracking-wider">Exercise</th>
              <th className="text-left py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Muscle Group</th>
              <th className="text-left py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Equipment</th>
              <th className="text-right py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Sets x Reps</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/30">
            {exercises.map((ex, i) => (
              <tr key={i} className="hover:bg-muted/30 transition-colors flex flex-col sm:table-row py-3 sm:py-0 px-5 sm:px-0">
                <td className="py-2 sm:py-3 sm:px-5"><div className="font-medium text-foreground">{ex.name}</div></td>
                <td className="py-1 sm:py-3 sm:px-5 hidden sm:table-cell"><span className="inline-flex items-center px-2 py-0.5 rounded-md bg-secondary/10 text-secondary text-xs font-semibold border border-secondary/20">{ex.muscle}</span></td>
                <td className="py-1 sm:py-3 sm:px-5 text-muted-foreground text-sm font-medium">{ex.equipment}</td>
                <td className="py-1 sm:py-3 sm:px-5 sm:text-right font-medium text-foreground">{ex.sets} x <span className="text-muted-foreground">{ex.reps}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
