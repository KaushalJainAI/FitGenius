import { Settings, RefreshCw, CheckCircle } from 'lucide-react';

export default function MyPlan() {
  return (
    <div className="bg-card border border-border overflow-hidden rounded-2xl shadow-card animate-slide-in-right flex flex-col h-full min-h-[70vh]">
      <div className="border-b border-border p-6 bg-muted/30 flex justify-between items-center px-6">
        <div>
          <h2 className="font-semibold text-xl uppercase flex gap-2 items-center">
            Your Optimized 3-Day Split (Weekly Plan)
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Hybrid Model (Content + Collaborative) • Sequential Logic Applied
          </p>
        </div>
        <div className="flex items-center gap-3">
           <div className="hidden sm:flex bg-secondary/10 text-secondary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-secondary/20 items-center justify-center">
             <CheckCircle size={14} className="mr-1 inline" /> High Confidence
           </div>
           <button className="h-10 w-10 flex items-center justify-center rounded-xl bg-muted/50 text-foreground hover:bg-muted transition-colors border border-border">
              <Settings className="h-5 w-5" />
           </button>
        </div>
      </div>

      <div className="p-6 space-y-6 flex-1 overflow-y-auto">
        <WorkoutDay 
          day="Day 1" 
          focus="Push (Chest, Shoulders, Triceps)" 
          colorClass="text-primary"
          exercises={[
              { name: "Barbell Bench Press", muscle: "Chest", equipment: "Barbell", sets: 3, reps: "8-10" },
              { name: "Overhead Shoulder Press", muscle: "Shoulders", equipment: "Dumbbells", sets: 4, reps: "10-12" },
              { name: "Tricep Dips", muscle: "Triceps", equipment: "Bodyweight", sets: 4, reps: "To failure" },
              { name: "Lateral Raises", muscle: "Shoulders", equipment: "Dumbbells", sets: 3, reps: "15" }
          ]}
        />
        
        {/* Muscle Group Rotation Notification box */}
        <div className="mx-6 border-l-2 border-primary pl-4 py-3 my-4 relative bg-primary/5 rounded-e-lg border-y border-r border-border backdrop-blur-sm">
          <div className="absolute -left-[3px] top-1/2 -translate-y-1/2 w-1.5 h-6 rounded-full bg-primary shadow-glow"></div>
          <p className="text-sm text-muted-foreground leading-relaxed flex items-start gap-2">
            <RefreshCw className="h-5 w-5 text-primary shrink-0 mt-0.5" />
            <span>
               <strong className="text-foreground">Sequence Logic:</strong> Push muscles heavily targeted. Day 2 shifts entirely to <strong className="text-foreground">Legs & Core</strong> to enforce 48-72h recovery for Push muscles, guaranteeing sequence completion probability and injury reduction.
            </span>
          </p>
        </div>

        <WorkoutDay 
          day="Day 2" 
          focus="Legs & Core" 
          colorClass="text-accent"
          exercises={[
              { name: "Barbell Squats", muscle: "Quads", equipment: "Barbell", sets: 4, reps: "6-8" },
              { name: "Romanian Deadlifts", muscle: "Hamstrings", equipment: "Barbell", sets: 3, reps: "10" },
              { name: "Bulgarian Split Squats", muscle: "Quads", equipment: "Dumbbells", sets: 3, reps: "10/leg" },
              { name: "Hanging Leg Raises", muscle: "Core", equipment: "Pull-up Bar", sets: 3, reps: "15" }
          ]}
        />
        
        <WorkoutDay 
          day="Day 3" 
          focus="Pull (Back, Biceps, Forearms)" 
          colorClass="text-secondary"
          exercises={[
              { name: "Weighted Pull-Ups", muscle: "Lats/Back", equipment: "Pull-up Bar", sets: 3, reps: "8-10" },
              { name: "Barbell Rows", muscle: "Back", equipment: "Barbell", sets: 3, reps: "10" },
              { name: "Dumbbell Hammer Curls", muscle: "Biceps", equipment: "Dumbbells", sets: 4, reps: "12" },
              { name: "Face Pulls", muscle: "Rear Delts", equipment: "Cable", sets: 3, reps: "15" }
          ]}
        />
      </div>
    </div>
  );
}

// Reusable component
function WorkoutDay({ day, focus, colorClass, exercises }: { day: string, focus: string, colorClass: string, exercises: any[] }) {
   return (
      <div className="border border-border/60 rounded-xl overflow-hidden hover-lift bg-background shadow-sm transition-all group">
         <div className="px-5 py-4 flex items-center gap-2 border-b border-border/60 bg-muted/20 group-hover:bg-muted/40 transition-colors">
            <h4 className="font-semibold flex items-center gap-2 text-foreground">
               <span className="bg-background px-2 py-0.5 rounded shadow-sm border border-border text-sm flex gap-1 items-center">
                  <span className="text-[12px]">☀️</span> <span className={colorClass}>{day}</span>
               </span>
               <span className="text-muted-foreground mx-1">/</span>
               <span className="tracking-wide">Focus: {focus}</span>
            </h4>
         </div>
         <div className="p-0 overflow-x-auto">
            <table className="w-full text-sm">
               <thead className="bg-background hidden sm:table-header-group">
                  <tr>
                     <th className="text-left py-3 px-5 font-semibold text-muted-foreground w-1/3 text-xs uppercase tracking-wider">Exercise</th>
                     <th className="text-left py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Muscle Group</th>
                     <th className="text-left py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Equipment</th>
                     <th className="text-right py-3 px-5 font-semibold text-muted-foreground text-xs uppercase tracking-wider">Sets × Reps</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-border/30">
                  {exercises.map((ex, i) => (
                     <tr key={i} className="hover:bg-muted/30 transition-colors flex flex-col sm:table-row py-3 sm:py-0 px-5 sm:px-0">
                        <td className="py-2 sm:py-3 sm:px-5">
                           <div className="font-medium text-foreground">{ex.name}</div>
                        </td>
                        <td className="py-1 sm:py-3 sm:px-5 hidden sm:table-cell">
                           <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-secondary/10 text-secondary text-xs font-semibold border border-secondary/20">
                              {ex.muscle}
                           </span>
                        </td>
                        <td className="py-1 sm:py-3 sm:px-5 text-muted-foreground text-sm font-medium">
                           {ex.equipment}
                        </td>
                        <td className="py-1 sm:py-3 sm:px-5 sm:text-right font-medium text-foreground">
                           {ex.sets} × <span className="text-muted-foreground">{ex.reps}</span>
                        </td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>
      </div>
   );
}
