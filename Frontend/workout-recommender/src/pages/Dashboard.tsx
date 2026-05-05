import React from 'react';
import { ArrowRight, Activity, Calendar, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6 stagger-children animate-fade-in-up">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard icon={<Activity />} label="Current Split" value="Push/Pull/Legs" />
        <StatCard icon={<Calendar />} label="Workouts Finished" value="12" />
        <StatCard icon={<Award />} label="BMI Status" value="Healthy (23.5)" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 h-full">
         <div className="bg-card border border-border p-6 rounded-2xl shadow-card relative overflow-hidden group hover-lift flex flex-col justify-between min-h-[300px]">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl -mr-10 -mt-10 transition-smooth group-hover:bg-primary/20"></div>
            <div>
               <h2 className="text-xl font-bold mb-2 text-foreground">Next Up: Day 1 (Push)</h2>
               <p className="text-muted-foreground max-w-sm">Chest, Shoulders & Triceps. Get ready to activate your upper body strength and build foundational muscle mass!</p>
            </div>
            
            <button 
               onClick={() => navigate('/plan')}
               className="mt-6 self-start flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-2.5 rounded-xl font-medium transition-all hover:gap-3"
            >
               View Workout <ArrowRight size={18} />
            </button>
         </div>

         <div className="bg-card border border-border p-6 rounded-2xl shadow-card flex flex-col items-center justify-center text-center min-h-[300px]">
            <div className="w-16 h-16 bg-secondary/10 text-secondary rounded-full flex items-center justify-center mb-4 border border-secondary/20">
               <Activity size={32} />
            </div>
            <h3 className="text-xl font-bold mb-2">Want to change your routine?</h3>
            <p className="text-muted-foreground max-w-sm text-sm mb-6">
               Recalibrate the recommender system with your updated fitness constraints and experience level.
            </p>
            <button 
               onClick={() => navigate('/profile')}
               className="border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground px-5 py-2.5 rounded-xl font-medium transition-colors w-full max-w-xs"
            >
               Update Profile
            </button>
         </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
   return (
      <div className="bg-card border border-border p-6 rounded-2xl shadow-sm flex items-center gap-4 hover-lift">
         <div className="w-14 h-14 bg-muted/50 rounded-xl flex items-center justify-center text-primary border border-primary/10">
            {icon}
         </div>
         <div>
            <p className="text-sm text-muted-foreground font-medium">{label}</p>
            <h3 className="text-2xl font-bold text-foreground tracking-tight">{value}</h3>
         </div>
      </div>
   );
}
